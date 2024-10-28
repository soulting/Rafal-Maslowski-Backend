import json
import os
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
SHEET_ID = os.getenv("SHEED_KEY")

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
client = gspread.authorize(credentials)
sheed = client.open_by_key(SHEET_ID)

# values = sheed.sheet1
print(int(sheed.sheet1.cell(2, 1).value) + 1)

# values = sheed.sheet1
# new_row = ['John', 'Doe', 'johndoe@example.com', 'Software Engineer']
# values.insert_row(new_row, index=2)
