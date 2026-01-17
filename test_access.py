import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "C:/Users/testi/AppData/Local/Programs/Python/Python313/11labtest1/service_account.json"
SHEET_ID = "1Vcc61nKPrBJrW6aM9eAnth3eLyKclSk62D3Skn9Kdqk"  

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)

try:
    sh = gc.open_by_key(SHEET_ID)
    print("Sheet opened successfully!")
except Exception as e:
    print("Error:", e) 

