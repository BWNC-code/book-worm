# import required libraries
import gspread
from google.oauth2.service_account import Credentials

#define scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

# add credentials to the account
CREDS = Credentials.from_json_keyfile_name('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)

# authorize the clientsheet
CLIENT = gspread.authorize(creds)

# get the instance of the Spreadsheet
SHEET = client.open('library').sheet1

