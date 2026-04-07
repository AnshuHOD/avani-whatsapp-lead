import requests
from config import COMBIRDS_API_KEY, COMBIRDS_BASE_URL, WELCOME_TEMPLATE_NAME, COMPANY_NAME

# Test parameters
phone = "918199820779"
name = "Anshu"
service_interest = "Want to know about your services?"

url = f"{COMBIRDS_BASE_URL}/v2"
headers = {"Content-Type": "application/json"}
payload = {
    "apiKey": COMBIRDS_API_KEY,
    "campaignName": WELCOME_TEMPLATE_NAME,
    "destination": phone,
    "userName": name,
    "templateParams": [name, service_interest, COMPANY_NAME],
    "source": "api"
}

print(f"Testing URL: {url}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
