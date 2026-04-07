import time
from sheets_handler import get_pending_leads, mark_as_sent
from combirds_handler import send_welcome_message

def process_pending_leads():
    print("🔍 Checking for pending leads...")
    try:
        pending = get_pending_leads()
    except Exception as e:
        print(f"❌ Error fetching leads: {e}")
        return

    if not pending:
        print("✅ No pending leads found.")
        return

    for lead in pending:
        name = lead.get("Name", "Valuable Customer")
        phone = lead.get("Phone", "")
        service = lead.get("Service_Interest", "General Enquiry")
        row_num = lead.get("_row_number")

        if not phone:
            print(f"⚠️ Skipping row {row_num} — no phone number")
            continue

        print(f"🚀 Sending welcome to {name} at {phone} for {service}...")
        lead_id = send_welcome_message(phone, name, service)

        if lead_id:
            mark_as_sent(row_num, lead_id)
            time.sleep(1)  # Small delay between messages — good practice

if __name__ == "__main__":
    # Option 2: Run every 60 seconds
    print("🤖 WhatsApp Automation Started...")
    while True:
        process_pending_leads()
        print("⏳ Waiting 60 seconds...")
        time.sleep(60)
