# import required libraries
import gspread
from google.oauth2.service_account import Credentials

# define scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

# add credentials to the account
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)

# authorize the clientsheet
CLIENT = gspread.authorize(SCOPED_CREDS)

# get the instance of the Spreadsheet
SHEET = CLIENT.open('book_worm').sheet1

# define the add_book function
def add_book():
    """
    Add new book to database
    """
    print("Enter the book details below:")
    title = input("Title: ")
    author = input("Author: ")
    year = input("Year (optional): ")
    genre = input("Genre: ")
    # add input validation here
    
    # add the book to the sheet
    SHEET.append_row([title, author, year, genre])
    print("Book added successfully!")


add_book()