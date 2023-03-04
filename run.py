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

# define the main menu function
def main_menu():
    print("Welcome to Book Inventory!")
    print("Please select an option below:")
    print("1. Add a book")
    print("2. Quit")
    choice = input("Enter your choice: ")
    return choice

# define the add_book function
def add_book():
    """
    Add new book to database
    """
    print("Enter the book details below:")
    fields = ["Title", "Author", "Year (optional)", "Genre"]
    book = []
    
    for field in fields:
        while True:
            value = input(f"{field}: ")
            if len(value) >= 2 and value.isalnum():
                book.append(value)
                break
            else:
                print(f"Invalid {field}. Please enter at least 2 alphanumeric characters.")
            
    # add the book to the sheet
    SHEET.append_row(book)
    print("Book added successfully!")


# define the main function
def main():
    while True:
        choice = main_menu()
        if choice == '1':
            add_book()
        elif choice == '2':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number")


# call main function

main()