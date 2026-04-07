import requests
import uuid
from config import COMBIRDS_API_KEY, COMBIRDS_BASE_URL, WELCOME_TEMPLATE_NAME, COMPANY_NAME

def send_welcome_message(phone, name, service_interest):
    """
    Send welcome WhatsApp message to a new lead using AiSensy v2 API format.
    """
    lead_id = str(uuid.uuid4())[:8].upper()

    # AiSensy v2 Campaign Endpoint
    url = f"{COMBIRDS_BASE_URL}/v2"

    headers = {
        "Content-Type": "application/json"
    }

    # AiSensy v2 Payload Structure
    payload = {
        "apiKey": COMBIRDS_API_KEY,
        "campaignName": WELCOME_TEMPLATE_NAME,
        "destination": str(phone),
        "userName": str(name),
        "templateParams": [
            str(name),
            str(service_interest),
            str(COMPANY_NAME)
        ],
        "source": "api"
    }

    print(f"DEBUG: Sending to {url} with campaign {WELCOME_TEMPLATE_NAME}...")

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Welcome message sent to {phone} ({name})")
            return lead_id
        else:
            print(f"❌ Failed to send to {phone}: {response.status_code} — {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception sending message to {phone}: {e}")
        return None

def send_reply_to_lead(phone, message):
    """
    Send a custom reply message to a lead.
    (Note: AiSensy single message API might differ, using the same campaign structure for now
    if you have a generic template for replies, otherwise this needs a different endpoint).
    """
    # For now, keeping it basic as per the standard AiSensy 'send message' if available.
    # Often it's the same v2/campaign but with a different template.
    print("⚠️ send_reply_to_lead might need a specific 'Reply' template in AiSensy.")
    return False
