from flask import Flask, request, jsonify
from datetime import datetime
from sheets_handler import save_reply

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """
    Combirds will POST to this endpoint whenever a lead replies.
    """
    data = request.json
    print(f"📩 Webhook received: {data}")

    try:
        # ⚠️ Adjust these keys based on actual Combirds webhook payload
        # Usually it's data['from'] or data['contacts'][0]['wa_id']
        # For message content: data['messages'][0]['text']['body']
        
        # This is a generic extraction logic based on common API patterns
        # Must be verified with real webhook data
        if "from" in data:
            phone = data["from"]
        elif "contacts" in data and len(data["contacts"]) > 0:
            phone = data["contacts"][0].get("wa_id", "")
        else:
            phone = ""

        message = ""
        if "message" in data and "text" in data["message"]:
            message = data["message"]["text"].get("body", "")
        elif "messages" in data and len(data["messages"]) > 0:
            msg_obj = data["messages"][0]
            if "text" in msg_obj:
                message = msg_obj["text"].get("body", "")

        if not phone or not message:
            print("⚠️ Missing phone or message in webhook payload")
            return jsonify({"status": "ignored", "reason": "missing data"}), 200

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_reply(phone, message, timestamp)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    print("🚀 Webhook Server Started on Port 5000...")
    app.run(port=5000, debug=True)
