import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import GOOGLE_SHEET_NAME, CREDENTIALS_FILE

def get_sheet():
    """Connect to Google Sheets using either a file or an environment variable JSON string."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # 1. Try loading from Environment Variable (FOR CLOUD DEPLOYMENT)
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            print("🔐 Auth: SUCCESS (Loaded from Environment Variable)")
        
        # 2. Try loading from File (FOR LOCAL TESTING)
        elif os.path.exists(CREDENTIALS_FILE):
                creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
                print(f"🔐 Auth: SUCCESS (Loaded from {CREDENTIALS_FILE})")
        
        else:
            raise FileNotFoundError("Neither GOOGLE_CREDENTIALS_JSON nor credentials.json found.")
            
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        return sheet
        
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return None

def get_pending_leads():
    """Fetch all rows where Status = Pending."""
    sheet = get_sheet()
    if not sheet:
        return []
    all_rows = sheet.get_all_records()
    pending = []
    for i, row in enumerate(all_rows, start=2):
        if row.get("Status", "").strip().lower() == "pending":
            row["_row_number"] = i
            pending.append(row)
    return pending

def mark_as_sent(row_number, lead_id):
    """Update Status to Sent."""
    sheet = get_sheet()
    if not sheet:
        return
    sheet.update_cell(row_number, 4, "Sent")
    sheet.update_cell(row_number, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sheet.update_cell(row_number, 8, lead_id)
    print(f"✅ Row {row_number} marked as Sent")

def save_reply(phone, message, timestamp):
    """Save lead's reply."""
    sheet = get_sheet()
    if not sheet:
        return False
    all_rows = sheet.get_all_records()
    for i, row in enumerate(all_rows, start=2):
        if str(row.get("Phone", "")).strip() == str(phone).strip():
            sheet.update_cell(i, 4, "Replied")
            sheet.update_cell(i, 6, message)
            sheet.update_cell(i, 7, timestamp)
            print(f"✅ Reply saved for {phone}")
            return True
    return False
