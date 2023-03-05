# import required libraries
import time
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
    """
    Displays options to user for each library function and returns choice
    """
    print("\033[2J\033[H")
    print("Welcome to Book Inventory!")
    print("Please select an option below:")
    print("1. Add a book")
    print("2. Remove a book")
    print("3. Update a book")
    print("4. Quit")
    choice = input("Enter your choice: ")
    return choice


# define the add_book function
def add_book():
    """
    Add new book to database
    """
    print("\033[2J\033[H")
    print("Enter the book details below:")
    fields = ["Title", "Author", "Year (optional)", "Genre"]
    book = []

    for i, field in enumerate(fields):
        while True:
            value = input(f"{field}: ")
            if i == 2 and value and not value.isdigit():
                print("Invalid year. Please enter digits only.")
            elif i == 2 and value == "":
                book.append("")
                break
            elif len(value) >= 2 and value.replace(" ", "").isalnum():
                book.append(value)
                break
            else:
                print(f"Invalid {field}. Please enter at least 2 alphanumeric characters.")
    # add the book to the sheet
    SHEET.append_row(book)
    print("Book added successfully!")
    time.sleep(2)


def remove_book():
    """
    Remove book from database
    """
    while True:
        print("\033[2J\033[H")
        title = input("Enter the title of the book you want to remove (q to return to main menu): \n")
        if title == 'q':
            return
        try:
            # find the book in the sheet
            cell = SHEET.find(title)
            # remove the book from the sheet
            SHEET.delete_rows(cell.row)
            print("Book removed successfully!")
            time.sleep(2)
            return
        except AttributeError:
            print("The book is not in the database. Please try again.")
            time.sleep(2)


def update_book():
    """
    Update existing book in database
    """
    while True:
        print("\033[2J\033[H")
        title = input("Enter the title of the book you want to update (q to return to main menu): \n")
        if title == 'q':
            return
        try:
            cell = SHEET.find(title)
        except AttributeError:
            print(f"The book '{title}' was not found in the database.")
            time.sleep(2)
            continue

        book_fields = ["Title", "Author", "Year", "Genre"]
        book_values = SHEET.row_values(cell.row)

        book_update = []
        for i, field in enumerate(book_fields):
            while True:
                value = input(f"Enter the new {field.lower()} (or press Enter to keep existing): ")
                if not value:
                    book_update.append(book_values[i])
                    break
                elif field == "Year" and not value.isdigit():
                    print("Invalid year format. Please enter a 4-digit year (YYYY).")
                elif len(value) < 2 or not value.replace(" ","").isalnum():
                    print(f"Invalid {field.lower()} format. Please enter at least 2 alphanumeric characters.")
                else:
                    book_update.append(value)
                    break
        for i, field in enumerate(book_fields):
            SHEET.update_cell(cell.row, i+1, book_update[i])
        print("Book updated successfully!")
        time.sleep(2)
        return

# define the main function
def main():
    """
    Main function runs at start
    """
    while True:
        choice = main_menu()
        if choice == '1':
            add_book()
        elif choice == '2':
            remove_book()
        elif choice == '3':
            update_book()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number")


# call main function

main()
