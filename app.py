import time
import threading
from flask import Flask, request, jsonify
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sheets_handler import get_pending_leads, mark_as_sent, save_reply
from combirds_handler import send_welcome_message
from config import COMPANY_NAME

app = Flask(__name__)

# --- SENDER LOGIC (Background Task) ---
def process_leads_job():
    """
    Function to check for pending leads every minute.
    """
    print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Checking for pending leads...")
    try:
        pending = get_pending_leads()
        if not pending:
            return

        for lead in pending:
            name = lead.get("Name", "Valuable Customer")
            phone = lead.get("Phone", "")
            service = lead.get("Service_Interest", "General Enquiry")
            row_num = lead.get("_row_number")

            if not phone:
                continue

            print(f"🚀 Sending welcome to {name} ({phone})...")
            lead_id = send_welcome_message(phone, name, service)

            if lead_id:
                mark_as_sent(row_num, lead_id)
                time.sleep(1)
    except Exception as e:
        print(f"❌ Error in background lead processing: {e}")

# Setup Background Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=process_leads_job, trigger="interval", seconds=60)
scheduler.start()

# --- WEBHOOK RECEIVER LOGIC ---
@app.route("/", methods=["GET"])
def home():
    return "Avani WhatsApp Bot is LIVE 24/7! 🤖", 200

@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """
    Receives replies from leads via Combirds/AiSensy.
    """
    data = request.json
    print(f"📩 Webhook received: {data}")

    try:
        # Generic payload extraction
        phone = ""
        if "from" in data:
            phone = data["from"]
        elif "contacts" in data and len(data["contacts"]) > 0:
            phone = data["contacts"][0].get("wa_id", "")

        message = ""
        if "message" in data and "text" in data["message"]:
            message = data["message"]["text"].get("body", "")
        elif "messages" in data and len(data["messages"]) > 0:
            msg_obj = data["messages"][0]
            if "text" in msg_obj:
                message = msg_obj["text"].get("body", "")

        if not phone or not message:
            return jsonify({"status": "ignored"}), 200

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_reply(phone, message, timestamp)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    # Local running (use gunicorn for production/hosting)
    print("🤖 Starting Avani WhatsApp Bot locally...")
    app.run(port=5000)
