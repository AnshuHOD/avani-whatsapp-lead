# WhatsApp Lead Automation — Avani Enterprises
### Stack: Python + Google Sheets + Combirds API

---

## What This System Does

```
New Lead Added to Sheet
        ↓
Python detects new row
        ↓
Combirds API sends WhatsApp Welcome Message
        ↓
Sheet updated → Status = "Sent"
        ↓
Lead replies on WhatsApp
        ↓
Combirds Webhook fires → Python receives it
        ↓
Reply saved back to Google Sheet
        ↓
Your team replies via script → Also logged in Sheet
```

---

## Part 1 — Google Sheet Setup

### Sheet Name: `Leads`

Create a Google Sheet with these exact columns:

| Column | Name | Description |
|--------|------|-------------|
| A | `Name` | Lead's full name |
| B | `Phone` | Phone with country code e.g. `919876543210` |
| C | `Service_Interest` | What they enquired about |
| D | `Status` | `Pending` / `Sent` / `Replied` |
| E | `Welcome_Sent_At` | Timestamp when welcome message was sent |
| F | `Last_Reply` | Last message received from lead |
| G | `Last_Reply_At` | Timestamp of that reply |
| H | `Lead_ID` | Unique ID (auto-filled by script) |

> **Tip:** Fill column D as `Pending` manually when you add a new lead. The script watches for `Pending` rows and processes them.

---

## Part 2 — Google Sheets API Setup

### Step 1 — Create a Google Cloud Project

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Click **New Project** → Name it `avani-whatsapp-bot`
3. Click **Create**

### Step 2 — Enable Google Sheets API

1. In the project, go to **APIs & Services → Library**
2. Search `Google Sheets API` → Click **Enable**
3. Also enable **Google Drive API**

### Step 3 — Create Service Account

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Name it `sheets-bot` → Click **Done**
4. Click on the service account → Go to **Keys** tab
5. Click **Add Key → Create new key → JSON**
6. A file downloads — rename it to `credentials.json`
7. Save it in your project folder

### Step 4 — Share Sheet with Service Account

1. Open your Google Sheet
2. Click **Share**
3. Paste the service account email (looks like `sheets-bot@avani-whatsapp-bot.iam.gserviceaccount.com`)
4. Give it **Editor** access → Click **Send**

---

## Part 3 — Project Folder Structure

```
avani_whatsapp_bot/
│
├── credentials.json          ← Google Service Account key
├── config.py                 ← All your API keys & settings
├── sheets_handler.py         ← Google Sheets read/write functions
├── combirds_handler.py       ← Combirds API functions
├── sender.py                 ← Main script: detects Pending leads & sends messages
├── webhook_receiver.py       ← Flask server: receives replies from Combirds
├── requirements.txt          ← Python dependencies
└── README.md
```

---

## Part 4 — Python Code

### `requirements.txt`

```
gspread
oauth2client
requests
flask
python-dotenv
```

Install with:
```bash
pip install -r requirements.txt
```

---

### `config.py`

```python
# config.py — Store all your credentials here

COMBIRDS_API_KEY = "your_combirds_api_key_here"
COMBIRDS_BASE_URL = "https://api.combirds.com"   # confirm exact URL from Combirds dashboard

GOOGLE_SHEET_NAME = "Leads"                       # exact name of your Google Sheet
CREDENTIALS_FILE = "credentials.json"

# Your WhatsApp template name (must be approved in Combirds)
WELCOME_TEMPLATE_NAME = "welcome_lead"

COMPANY_NAME = "Avani Enterprises"
```

> **Note:** Never commit this file to GitHub. Add it to `.gitignore`.

---

### `sheets_handler.py`

```python
# sheets_handler.py — All Google Sheets operations

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import GOOGLE_SHEET_NAME, CREDENTIALS_FILE


def get_sheet():
    """Connect to Google Sheets and return the worksheet."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet


def get_pending_leads():
    """Fetch all rows where Status = Pending."""
    sheet = get_sheet()
    all_rows = sheet.get_all_records()
    pending = []
    for i, row in enumerate(all_rows, start=2):  # start=2 because row 1 is header
        if row.get("Status", "").strip().lower() == "pending":
            row["_row_number"] = i
            pending.append(row)
    return pending


def mark_as_sent(row_number, lead_id):
    """Update Status to Sent and record timestamp."""
    sheet = get_sheet()
    sheet.update_cell(row_number, 4, "Sent")                           # Column D = Status
    sheet.update_cell(row_number, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Column E
    sheet.update_cell(row_number, 8, lead_id)                          # Column H = Lead_ID
    print(f"✅ Row {row_number} marked as Sent")


def save_reply(phone, message, timestamp):
    """Find the lead by phone number and save their reply."""
    sheet = get_sheet()
    all_rows = sheet.get_all_records()
    for i, row in enumerate(all_rows, start=2):
        if str(row.get("Phone", "")).strip() == str(phone).strip():
            sheet.update_cell(i, 4, "Replied")                          # Column D = Status
            sheet.update_cell(i, 6, message)                            # Column F = Last_Reply
            sheet.update_cell(i, 7, timestamp)                          # Column G = Last_Reply_At
            print(f"✅ Reply saved for phone {phone}")
            return True
    print(f"⚠️ Phone {phone} not found in sheet")
    return False
```

---

### `combirds_handler.py`

```python
# combirds_handler.py — All Combirds API calls

import requests
import uuid
from config import COMBIRDS_API_KEY, COMBIRDS_BASE_URL, WELCOME_TEMPLATE_NAME, COMPANY_NAME


def send_welcome_message(phone, name, service_interest):
    """
    Send welcome WhatsApp message to a new lead.
    Adjust the endpoint and payload format based on your Combirds API docs.
    """
    lead_id = str(uuid.uuid4())[:8].upper()  # Generate a short unique ID e.g. "A3F9B2C1"

    url = f"{COMBIRDS_BASE_URL}/v1/messages/send"   # ← confirm this endpoint from Combirds docs

    headers = {
        "Authorization": f"Bearer {COMBIRDS_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": phone,
        "type": "template",
        "template": {
            "name": WELCOME_TEMPLATE_NAME,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": name},
                        {"type": "text", "text": service_interest},
                        {"type": "text", "text": COMPANY_NAME}
                    ]
                }
            ]
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"✅ Welcome message sent to {phone} ({name})")
        return lead_id
    else:
        print(f"❌ Failed to send to {phone}: {response.status_code} — {response.text}")
        return None


def send_reply_to_lead(phone, message):
    """Send a custom reply message to a lead (used by your team)."""
    url = f"{COMBIRDS_BASE_URL}/v1/messages/send"

    headers = {
        "Authorization": f"Bearer {COMBIRDS_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"✅ Reply sent to {phone}")
        return True
    else:
        print(f"❌ Failed: {response.status_code} — {response.text}")
        return False
```

---

### `sender.py` — Main Script (Run this to process Pending leads)

```python
# sender.py — Detects Pending leads and sends WhatsApp welcome messages

import time
from sheets_handler import get_pending_leads, mark_as_sent
from combirds_handler import send_welcome_message

def process_pending_leads():
    print("🔍 Checking for pending leads...")
    pending = get_pending_leads()

    if not pending:
        print("✅ No pending leads found.")
        return

    for lead in pending:
        name = lead.get("Name", "")
        phone = lead.get("Phone", "")
        service = lead.get("Service_Interest", "General Enquiry")
        row_num = lead.get("_row_number")

        if not phone:
            print(f"⚠️ Skipping row {row_num} — no phone number")
            continue

        lead_id = send_welcome_message(phone, name, service)

        if lead_id:
            mark_as_sent(row_num, lead_id)
            time.sleep(1)  # Small delay between messages — good practice


if __name__ == "__main__":
    # Option 1: Run once
    process_pending_leads()

    # Option 2: Run every 60 seconds (uncomment below, comment above)
    # while True:
    #     process_pending_leads()
    #     print("⏳ Waiting 60 seconds...")
    #     time.sleep(60)
```

---

### `webhook_receiver.py` — Flask Server (Receives replies from leads)

```python
# webhook_receiver.py — Listens for incoming WhatsApp replies via Combirds webhook

from flask import Flask, request, jsonify
from datetime import datetime
from sheets_handler import save_reply

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """
    Combirds will POST to this endpoint whenever a lead replies.
    Adjust field names based on Combirds webhook payload format.
    """
    data = request.json
    print(f"📩 Webhook received: {data}")

    try:
        # ⚠️ Adjust these keys based on actual Combirds webhook payload
        phone = data["from"]                          # Lead's phone number
        message = data["message"]["text"]["body"]     # Their reply text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_reply(phone, message, timestamp)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(port=5000, debug=True)
```

---

## Part 5 — Combirds Webhook Configuration

For Combirds to send replies to your Flask server, you need to register a **Webhook URL** in Combirds dashboard.

### If running locally (for testing):

1. Install **ngrok**: [https://ngrok.com](https://ngrok.com)
2. Run your Flask server:
   ```bash
   python webhook_receiver.py
   ```
3. In a new terminal, run:
   ```bash
   ngrok http 5000
   ```
4. Copy the HTTPS URL it gives, e.g. `https://abc123.ngrok.io`
5. In Combirds Dashboard → Settings → Webhook → paste:
   ```
   https://abc123.ngrok.io/webhook
   ```

### For Production (when deploying):

Deploy `webhook_receiver.py` to a server (Railway, Render, or VPS) and use that URL instead of ngrok.

---

## Part 6 — WhatsApp Message Template

In your **Combirds Dashboard**, create an approved template like this:

- **Template Name:** `welcome_lead`
- **Category:** `UTILITY`
- **Language:** English
- **Body:**
  ```
  Hello {{1}}! 👋

  Thank you so much for choosing *Avani Enterprises*! 🎉

  We have received your enquiry regarding *{{2}}*.

  Our team will connect with you very soon. Feel free to reply here if you have any questions!

  — Team {{3}}
  ```
  - `{{1}}` = Lead Name
  - `{{2}}` = Service Interest
  - `{{3}}` = Company Name

> Templates must be approved by WhatsApp (via Combirds) before they can be used. Approval usually takes a few hours.

---

## Part 7 — How to Run Everything

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Add your credentials
- Put `credentials.json` in the project folder
- Fill in `config.py` with your Combirds API key

### Step 3 — Add a test lead to your Google Sheet
Fill in one row manually with:
- Name: `Test Lead`
- Phone: `919XXXXXXXXX`
- Service_Interest: `Digital Marketing`
- Status: `Pending`

### Step 4 — Run the sender
```bash
python sender.py
```
→ It will detect the `Pending` row, send a WhatsApp message, and update Status to `Sent`

### Step 5 — Start the webhook server
```bash
python webhook_receiver.py
```
→ When the lead replies, their message will be saved back to the sheet automatically

---

## Part 8 — Summary Flow

```
You add lead to Sheet (Status = Pending)
            ↓
python sender.py runs
            ↓
Finds Pending row → Calls Combirds API
            ↓
WhatsApp message sent to lead ✅
            ↓
Sheet updated → Status = "Sent"
            ↓
Lead replies on WhatsApp
            ↓
Combirds fires webhook → hits /webhook endpoint
            ↓
Flask saves reply to Sheet → Status = "Replied" ✅
```

---

## Important Notes

| Topic | Note |
|-------|------|
| API Endpoint | Confirm exact Combirds API URL from their dashboard/docs |
| Webhook Payload | Print `data` in webhook to see exact field names Combirds sends |
| Template Approval | Must be approved before sending — do this first |
| Phone Format | Always use country code, no `+`, no spaces e.g. `919876543210` |
| Rate Limits | Add `time.sleep(1)` between bulk sends to avoid API throttling |
| Production | Use a proper server (not ngrok) for live deployment |

---

*Built for Avani Enterprises — Python + Google Sheets + Combirds WhatsApp API*
