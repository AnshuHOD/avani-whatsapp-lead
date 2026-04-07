import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Combirds API Configuration
COMBIRDS_API_KEY = os.getenv("COMBIRDS_API_KEY", "your_combirds_api_key_here")
COMBIRDS_BASE_URL = os.getenv("COMBIRDS_BASE_URL", "https://api.combirds.com")
WELCOME_TEMPLATE_NAME = os.getenv("WELCOME_TEMPLATE_NAME", "welcome_lead")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Avani Enterprises")

# Google Sheets Configuration
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Leads")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
