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
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        elif os.path.exists(CREDENTIALS_FILE):
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        else:
            return None
            
        client = gspread.authorize(creds)
        spreadsheet = client.open(GOOGLE_SHEET_NAME)
        return spreadsheet.get_worksheet(0) # Get the first tab
        
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return None

def get_pending_leads():
    """Fetch all rows where Status = Pending using a more robust method."""
    sheet = get_sheet()
    if not sheet:
        print("❌ Could not connect to sheet.")
        return []
        
    try:
        # Get all records as a list of dicts
        records = sheet.get_all_records(expected_headers=['Name', 'Phone', 'Service_Interest', 'Status'])
        pending = []
        
        # In get_all_records, the first data row (Excel Row 2) is index 0
        for i, row in enumerate(records):
            status = str(row.get("Status", "")).strip().lower()
            if status == "pending":
                row_data = row.copy()
                row_data["_row_number"] = i + 2 # Convert index to Excel row number
                pending.append(row_data)
        
        print(f"📊 Found {len(pending)} pending leads.")
        return pending
    except Exception as e:
        print(f"❌ Error reading records: {e}")
        # Fallback to general read if headers don't match exactly
        all_values = sheet.get_all_values()
        headers = all_values[0]
        try:
            status_idx = headers.index("Status")
        except:
            return []
            
        pending = []
        for i, row in enumerate(all_values[1:], start=2):
            if row[status_idx].strip().lower() == "pending":
                data = dict(zip(headers, row))
                data["_row_number"] = i
                pending.append(data)
        return pending

def mark_as_sent(row_number, lead_id):
    """Update Status to Sent."""
    sheet = get_sheet()
    if not sheet:
        return
    try:
        sheet.update_cell(row_number, 4, "Sent")
        sheet.update_cell(row_number, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sheet.update_cell(row_number, 8, lead_id)
        print(f"✅ Row {row_number} marked as Sent in sheet.")
    except Exception as e:
        print(f"❌ Error marking as sent: {e}")

def save_reply(phone, message, timestamp):
    """Save lead's reply."""
    sheet = get_sheet()
    if not sheet:
        return False
    try:
        records = sheet.get_all_records()
        for i, row in enumerate(records, start=2):
            if str(row.get("Phone", "")).strip() == str(phone).strip():
                sheet.update_cell(i, 4, "Replied")
                sheet.update_cell(i, 6, message)
                sheet.update_cell(i, 7, timestamp)
                return True
    except:
        pass
    return False
