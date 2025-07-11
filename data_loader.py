import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json

def load_data(source, csv_path=None, sheet_id=None, credentials_path=None):
    try:
        if source == "google_sheet":
            print(f"🔍 Loading from Google Sheet: {sheet_id}")
            print(f"🔑 Using credentials: {credentials_path}")

            creds = Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            gc = gspread.authorize(creds)
            sheet = gc.open_by_key(sheet_id)
            worksheet = sheet.sheet1
            records = worksheet.get_all_records()
            print(f"✅ Sheet loaded. Total records: {len(records)}")
            return records

        elif source == "csv":
            print(f"🔍 Loading from CSV: {csv_path}")
            df = pd.read_csv(csv_path)
            return df.to_dict(orient="records")

        else:
            print("❌ Unknown data source")
            return None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
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
