import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json

def load_data(source="google_sheet", csv_path=None, sheet_id=None, credentials_path=None):
    """
    Load data from either CSV file or Google Sheets.
    
    Args:
        source: "csv" or "google_sheet"
        csv_path: Path to CSV file (if source is "csv")
        sheet_id: Google Sheets ID (if source is "google_sheet")
        credentials_path: Path to Google credentials JSON file
    
    Returns:
        List of dictionaries with 'tamil' and 'arwi' keys
    """
    
    if source == "csv":
        try:
            if not csv_path or not os.path.exists(csv_path):
                print(f"CSV file not found: {csv_path}")
                return None
            
            df = pd.read_csv(csv_path)
            
            # Ensure required columns exist
            if 'tamil' not in df.columns or 'arwi' not in df.columns:
                print("CSV must contain 'tamil' and 'arwi' columns")
                return None
            
            # Convert to list of dictionaries
            data = []
            for _, row in df.iterrows():
                data.append({
                    'tamil': str(row['tamil']),
                    'arwi': str(row['arwi'])
                })
            
            return data
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return None
    
    elif source == "google_sheet":
        try:
            if not sheet_id or not credentials_path:
                print("Google Sheets requires sheet_id and credentials_path")
                return None
            
            if not os.path.exists(credentials_path):
                print(f"Credentials file not found: {credentials_path}")
                return None
            
            # Set up Google Sheets API
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            sheet = client.open_by_key(sheet_id).sheet1
            
            # Get all records
            records = sheet.get_all_records()
            
            if not records:
                print("No data found in Google Sheet")
                return None
            
            # Convert to required format
            data = []
            for record in records:
                # Handle different possible column names
                tamil_text = record.get('tamil') or record.get('Tamil') or record.get('TAMIL')
                arwi_text = record.get('arwi') or record.get('Arwi') or record.get('ARWI')
                
                if tamil_text and arwi_text:
                    data.append({
                        'tamil': str(tamil_text),
                        'arwi': str(arwi_text)
                    })
            
            return data
            
        except Exception as e:
            print(f"Error loading Google Sheets data: {e}")
            return None
    
    else:
        print(f"Unsupported data source: {source}")
        return None

# Test function
if __name__ == "__main__":
    # Test CSV loading
    csv_data = load_data(source="csv", csv_path="data/tamil_arwi.csv")
    if csv_data:
        print(f"Loaded {len(csv_data)} records from CSV")
        print("Sample record:", csv_data[0])
    
    # Test Google Sheets loading
    sheet_data = load_data(
        source="google_sheet",
        sheet_id="1CfwdVRxTf5HBErNRK9MIa6lPyzI_Zb_mBJ_nl4YsKxU",
        credentials_path="credentials.json"
    )
    if sheet_data:
        print(f"Loaded {len(sheet_data)} records from Google Sheets")
        print("Sample record:", sheet_data[0])