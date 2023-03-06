# import required libraries
import time
import math
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
    print("4. Display all books")
    print("5. Quit")
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


# define the remove_book function
def remove_book():
    """
    Remove book from database
    """
    while True:
        print("\033[2J\033[H")
        title = input("Enter the title of the book you want to remove\n(q to return to main menu): ")
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


# define the update_book function
def update_book():
    """
    Update existing book in database
    """
    while True:
        print("\033[2J\033[H")
        title = input("Enter the title of the book you want to update\n (q to return to main menu): ")
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
                elif len(value) < 2 or not value.replace(" ", "").isalnum():
                    print(f"Invalid {field.lower()} format. Please enter at least 2 alphanumeric characters.")
                else:
                    book_update.append(value)
                    break
        for i, field in enumerate(book_fields):
            SHEET.update_cell(cell.row, i+1, book_update[i])
        print("Book updated successfully!")
        time.sleep(2)
        return


def display_page(headers, data, page_number):
    """
    Display a single page of books
    """
    # calculate the start and end indices of the page
    start_index = (page_number - 1) * 10
    end_index = start_index + 10
    # display the headers
    print("\033[2J\033[H")
    print("\t".join(headers))
    print("=" * 80)
    # display the data for the page
    for row in data[start_index:end_index]:
        print("\t".join(row))
    print("=" * 80)

# define the display_books function
def display_books():
    """
    Display books in the database, splitting into pages of 10 with user controls to navigate pages or q to quit
    """
    # get all the values in the sheet
    values = SHEET.get_all_values()

    # extract the headers and data
    headers = values[0]
    data = values[1:]

    # get the total number of pages
    total_pages = math.ceil(len(data) / 10)

    # set the initial page to 1
    current_page = 1

    # display the first page
    display_page(headers, data, current_page)

    # loop until the user quits
    while True:
        # get the user's input
        choice = input(f"Page {current_page} of {total_pages}. Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ")
        # handle the user's input
        if choice == 'n' and current_page < total_pages:
            current_page += 1
            display_page(headers, data, current_page)
        elif choice == 'p' and current_page > 1:
            current_page -= 1
            display_page(headers, data, current_page)
        elif choice == 'q':
            break
        else:
            print("Invalid input. Please enter 'n', 'p', or 'q'.")



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
            display_books()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number")


# call main function

main()
