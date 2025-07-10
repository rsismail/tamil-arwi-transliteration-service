import base64
import os
import arabic_reshaper
from bidi import get_display
import pandas as pd
from flask import Flask, request, jsonify
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
from data_loader import load_data  # Import the load_data function
from logger import log_data  # Import the log_data function
from flask_cors import CORS
import tempfile

# Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load Gemini API key from environment
API_KEY = os.environ.get('GEMINI_API_KEY')
print(f"✅ API Key loaded: {'Yes' if API_KEY else 'No'}")

# Temp file paths
LOG_FILE = os.path.join(tempfile.gettempdir(), "output.log")
OUTPUT_FILE = os.path.join(tempfile.gettempdir(), "temp_output.txt")
TEMP_INPUT_FILE = os.path.join(tempfile.gettempdir(), "temp_input.txt")


@app.route("/", methods=["GET"])
def health():
    """Health check route."""
    return jsonify({"status": "OK", "api_key_loaded": bool(API_KEY)})


def generate_text(tamil_input, data_source="google_sheet"):
    """Generates Arwi text from Tamil input using the Gemini API."""

    if not API_KEY:
        return "Error: API key not found. Please set GEMINI_API_KEY environment variable.", 500

    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.0-flash"

    # Load data
    if data_source == "csv":
        data_path = "data/tamil_arwi.csv"
        credentials_path = None
    elif data_source == "google_sheet":
        data_path = "1CfwdVRxTf5HBErNRK9MIa6lPyzI_Zb_mBJ_nl4YsKxU"
        credentials_path = "credentials.json"
    else:
        return "Error: Invalid data source.", 400

    data = load_data(
        source=data_source,
        csv_path=data_path,
        sheet_id=data_path,
        credentials_path=credentials_path,
    )

    if not data:
        return "Error: Failed to load data.", 500

    # Read temporary input file if exists
    try:
        with open(TEMP_INPUT_FILE, "r", encoding="utf-8") as f:
            temp_input_content = f.read().strip()
            if temp_input_content:
                tamil_input = temp_input_content
                print(f"Using input from {TEMP_INPUT_FILE}")
            else:
                print(f"{TEMP_INPUT_FILE} is empty, using request input.")
    except FileNotFoundError:
        print(f"{TEMP_INPUT_FILE} not found, using request input.")
    except Exception as e:
        print(f"Error reading {TEMP_INPUT_FILE}: {e}")

    # Build prompt
    examples = ""
    for row in data:
        tamil = row["tamil"]
        arwi = row["arwi"]
        examples += f"Tamil: {tamil}, Arwi: {arwi}\n"

    prompt = f"""You are an expert in transliterating Tamil text to Arwi script.
Don't add any sentence before or after the output text.
Here are a few examples:
{examples}
Now, transliterate the following Tamil text to Arwi:
Tamil: {tamil_input} Arwi:"""

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain"
    )

    output_text = ""
    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config
        ):
            output_text += chunk.text
    except Exception as e:
        return f"Error during Gemini API call: {e}", 500

    output_text = output_text.replace('\n', '')
    log_data(LOG_FILE, tamil_input, data_source, output_text, OUTPUT_FILE)

    return output_text, 200


@app.route('/transliterate', methods=['POST'])
def transliterate():
    data = request.get_json()
    tamil_input = data.get('tamil_input')
    data_source = data.get('data_source', 'google_sheet')

    if not tamil_input:
        return jsonify({"error": "Tamil input is required."}), 400

    output_text, status_code = generate_text(tamil_input, data_source)
    if status_code == 200:
        return jsonify({"output": output_text})
    else:
        return jsonify({"error": output_text}), status_code


if __name__ == '__main__':
    app.run(debug=True)
