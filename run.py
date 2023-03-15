"""import required libraries"""
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from termcolor import cprint
from inquirer import prompt, List
from inquirer.themes import GreenPassion
from tabulate import tabulate
import argon2
from gspread.exceptions import APIError
from googleapiclient.errors import HttpError

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
MAIN_SHEET = CLIENT.open('book_worm')

# Initialize the Argon2 password hasher
password_hasher = argon2.PasswordHasher()


# Create a new user account
def create_user():
    """
    Create a new user account with a new sheet in CLIENT and add the user's
    username and hashed password to the 'users' sheet.
    """
    # Get the 'users' sheet
    users_sheet = CLIENT.open('book_worm').worksheet('users')

    # Get the new user's information
    try:
        while True:
            print("\033[2J\033[H")
            cprint("CREATE A NEW USER", "green", attrs=["bold"])
            print(" ")
            cprint("PRESS CTRL+C TO CANCEL", "green", attrs=["bold"])
            username = input("Enter a username: \n")
            if len(username) < 4:
                print("Username must have at least 4 characters."
                      " Please try again.")
                time.sleep(2)
                continue
            password = input("Password: \n")
            confirm_password = input("Confirm password: \n")
            if len(password) < 8:
                print("Password must have at least 8 characters."
                      " Please try again.")
                time.sleep(2)
            elif password != confirm_password:
                print("Passwords do not match. Please try again.")
                time.sleep(2)
            else:
                break
    except (KeyboardInterrupt, EOFError):
        print("\nUser creation cancelled.")
        time.sleep(2)
        return

    # Hash the password using Argon2
    hashed_password = password_hasher.hash(password)

    # Try to create a new sheet for the user
    try:
        new_sheet = MAIN_SHEET.add_worksheet(
            title=username, rows="100", cols="20")
        new_sheet.update('A1', 'Title')
        new_sheet.update('B1', 'Author')
        new_sheet.update('C1', 'Year Published')
        new_sheet.update('D1', 'Genre')
    except APIError:
        print("Error: a sheet with that name already exists")
        time.sleep(2)
        return
    except HttpError as error:
        print(f"An error occurred: {error}")
        time.sleep(2)
        return

    # Add the user's information to the 'users' sheet
    users_sheet.append_row([username, hashed_password])
    print("User account created successfully!")
    time.sleep(2)
    return


def login():
    """
    Log in to an existing user account and set SHEET as their sheet in
    book_worm.
    """
    # Get the 'users' sheet
    users_sheet = CLIENT.open('book_worm').worksheet('users')

    print("\033[2J\033[H")
    cprint("LOGIN TO YOUR LIBRARY", "green", attrs=["bold"])
    print(" ")
    cprint("PRESS CTRL+C TO CANCEL", "green", attrs=["bold"])

    try:
        # Get the username and password from the user
        username = input("Enter your username: ")
        password = input("Enter your password: ")
    except KeyboardInterrupt:
        return "Q"

    # Try to find the user's information in the 'users' sheet
    user_cell = users_sheet.find(username)
    if not user_cell:
        print("Error: username not found")
        return False

    # Get the row and column indices of the user's information
    row_index = user_cell.row
    password_col = user_cell.col + 1

    # Check the password using Argon2
    password_hash = users_sheet.cell(row_index, password_col).value

    try:
        password_hasher.verify(password_hash, password)
    except (ValueError, argon2.exceptions.VerifyMismatchError):
        print("Error: incorrect password")
        return False

    # Set SHEET as the user's sheet in book_worm
    try:
        global SHEET
        SHEET = CLIENT.open('book_worm').worksheet(username)
    except APIError:
        print("Error: unable to access the user's sheet")
        return False

    print("Logged in successfully!")
    time.sleep(2)
    return True


# define the main menu function
def main_menu():
    """
    Displays options to user for each library function and returns choice
    """
    print("\033[2J\033[H")
    cprint("Welcome to BookWorm!", "yellow")
    print(" ")

    questions = [
        List('choice',
             message="Please select an option below:",
             choices=[('Add a book', '1'),
                      ('Remove a book', '2'),
                      ('Update a book', '3'),
                      ('Search for a book', '4'),
                      ('Display all books', '5'),
                      ('Quit', '6')
                      ]
             ),
    ]

    choice = prompt(questions, theme=GreenPassion())
    return choice['choice']


# define the add_book function
def add_book():
    """
    Add new book to database
    """
    print("\033[2J\033[H")
    cprint("ADD NEW BOOK", "green", attrs=["bold"])
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
                print(
                    f"Invalid {field}. Minimum 2 alphanumeric characters."
                    )
    # add the book to the sheet
    SHEET.append_row(book)
    print("Book added successfully!")
    time.sleep(2)

    # ask user if they want to add another book
    while True:
        choice = input("Do you want to add another book? (y/n): ")
        if choice.lower() == 'n':
            return
        elif choice.lower() == 'y':
            break
        else:
            cprint("Invalid choice. Please enter 'y' or 'n'.", "red")


# define add_book_isbn function
def add_book_isbn():
    """
    Look up book details using an ISBN and add the book to the database
    """
    while True:
        print("\033[2J\033[H")
        cprint("ADD BOOK BY ISBN", "green", attrs=["bold"])
        print("Enter 'q' at any time to quit\n")

        isbn = input("Enter the book's ISBN: ")
        if isbn == 'q':
            return

        try:
            # Call Google Books API to retrieve book details
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            book_data = response.json()["items"][0]["volumeInfo"]

            # Extract book information from the API response
            title = book_data["title"]
            authors = ", ".join(book_data.get("authors", ["Unknown"]))
            year = book_data.get("publishedDate", "Unknown")[:4]
            genres = ", ".join(book_data.get("categories", ["Unknown"]))

            # Add the book to the sheet
            SHEET.append_row([title, authors, year, genres])

            # Print out the information
            print(f"{title} by {authors} added successfully!")
            time.sleep(2)

            # ask user if they want to add another book
            while True:
                choice = input("Do you want to add another book? (y/n): ")
                if choice.lower() == 'n':
                    return
                elif choice.lower() == 'y':
                    break
                else:
                    cprint("Invalid choice. Please enter 'y' or 'n'.", "red")

        except requests.exceptions.HTTPError:
            print("Book not found")
            time.sleep(2)
            continue
        except KeyError:
            print("Invalid ISBN. Please try again.")
            time.sleep(2)
            continue


def add_book_menu():
    """
    Display the add book menu and prompt user for choice
    """
    while True:
        print("\033[2J\033[H")
        cprint("ADD BOOK", "green", attrs=["bold"])
        print(" ")

        questions = [
            List(
                "choice",
                message="How would you like to add a book?",
                choices=[
                    ("Add book manually", "1"),
                    ("Look up book by ISBN", "2"),
                    ("Quit", "q")
                ],
            ),
        ]
        answers = prompt(questions, theme=GreenPassion())
        choice = answers["choice"]
        if choice == '1':
            add_book()
            return
        elif choice == '2':
            add_book_isbn()
            return
        elif choice == 'q':
            return
        else:
            print("Invalid choice. Please enter 1 or 2.")
            time.sleep(2)


# define the remove_book function
def remove_book():
    """
    Remove book from database
    """
    while True:
        print("\033[2J\033[H")
        cprint("REMOVE BOOK FROM DATABASE", "green", attrs=["bold"])
        title = input("Enter the title of the book you want to remove\n"
                      "(q to return to main menu): ")
        if title == 'q':
            return
        try:
            # find the book in the sheet
            cell = SHEET.find(title)
            # remove the book from the sheet
            SHEET.delete_rows(cell.row)
            print("Book removed successfully!")
            time.sleep(2)

            # ask user if they want to remove another book
            while True:
                choice = input("Do you want to remove another book? (y/n): ")
                if choice.lower() == 'n':
                    return
                elif choice.lower() == 'y':
                    break
                else:
                    cprint("Invalid choice. Please enter 'y' or 'n'.", "red")
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
        cprint("UPDATE BOOK IN DATABASE", "green", attrs=["bold"])
        title = input("Enter the title of the book you want to update\n"
                      " (q to return to main menu): ")
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
                value = input(f"Enter the new {field.lower()} "
                              "(or press Enter to keep existing): ")
                if not value:
                    book_update.append(book_values[i])
                    break
                elif field == "Year" and not value.isdigit():
                    print("Invalid year format."
                          " Please enter a 4-digit year (YYYY).")
                elif len(value) < 2 or not value.replace(" ", "").isalnum():
                    print(f"Invalid {field.lower()} format."
                          " Please enter at least 2 alphanumeric characters.")
                else:
                    book_update.append(value)
                    break
        for i, field in enumerate(book_fields):
            SHEET.update_cell(cell.row, i+1, book_update[i])
        print("Book updated successfully!")
        time.sleep(2)
        return


def display_search(matching_books):
    """
    Display books in a formatted manner
    """
    page_size = 6
    page_number = 0
    num_pages = (len(matching_books) + page_size - 1) // page_size

    while True:
        print("\033[2J\033[H")
        start_index = page_number * page_size
        end_index = min(start_index + page_size, len(matching_books))
        page_books = matching_books[start_index:end_index]

        data = [[book['title'],
                 book['author'],
                 book['genre'],
                 book['year']
                 ] for book in page_books]
        headers = ['Title', 'Author', 'Genre', 'Year']
        print(tabulate(
                        data,
                        headers=headers,
                        tablefmt='fancy_grid',
                        maxcolwidths=20
                        ))

        if num_pages > 1:
            print(f"\nPage {page_number + 1}/{num_pages}\n")

        choices = ['Next page', 'Previous page', 'Quit']
        if page_number == 0:
            choices.remove('Previous page')
        if page_number == num_pages - 1:
            choices.remove('Next page')

        answer = prompt([
            List('answer',
                 message="Choose an option:",
                 choices=choices),
        ], theme=GreenPassion())['answer']

        if answer == 'Next page':
            page_number += 1
        elif answer == 'Previous page':
            page_number -= 1
        else:
            return


def search_books_by_title(title):
    """
    Search for books in the database by title
    """
    if title == '':
        return
    else:
        matching_books = []
        for row in SHEET.get_all_records():
            if title.lower() in row['Title'].lower():
                matching_books.append({
                    'title': row['Title'],
                    'author': row['Author'],
                    'genre': row['Genre'],
                    'year': row['Year Published']
                })
        if matching_books:
            display_search(matching_books)
        else:
            print(f"No books found with the title {title}.")
            time.sleep(2)


def search_books_by_author(author):
    """
    Search for books in the database by author name
    """
    if author == '':
        return
    else:
        matching_books = []
        for row in SHEET.get_all_records():
            if author.lower() in row['Author'].lower():
                matching_books.append({
                    'title': row['Title'],
                    'author': row['Author'],
                    'genre': row['Genre'],
                    'year': row['Year Published']
                })
        if matching_books:
            display_search(matching_books)
        else:
            print(f"No books found with the author {author}.")
            time.sleep(2)


def search_books_by_genre(genre):
    """
    Display books in the database that match the given genre
    """
    if genre == '':
        return
    else:
        matching_books = []
        for row in SHEET.get_all_records():
            if genre.lower() in row['Genre'].lower():
                matching_books.append({
                    'title': row['Title'],
                    'author': row['Author'],
                    'genre': row['Genre'],
                    'year': row['Year Published']
                })
        if matching_books:
            display_search(matching_books)
        else:
            print(f"No books found in genre '{genre}'.")
            time.sleep(2)


def search_menu():
    """
    Displays a search menu with options to search for books by author or genre
    Returns:
        str: The user's choice as a string.
    """
    print("\033[2J\033[H")
    cprint("SEARCH FOR BOOKS", "green", attrs=["bold"])
    print(" ")
    questions = [
            List(
                "choice",
                message="What would you like to search for?",
                choices=[
                    ("Search by Title", "1"),
                    ("Search by Author", "2"),
                    ("Search by Genre", "3"),
                    ("Quit", "q")
                ],
            ),
        ]
    answers = prompt(questions, theme=GreenPassion())
    choice = answers["choice"]
    return choice


def search_choice():
    """
    Handles the user's search choice.
    """
    while True:
        choice = search_menu()

        if choice == '1':
            title = input("Enter the title"
                          " (just hit enter to go back): ")
            if title == "":
                continue
            else:
                search_books_by_title(title)

        if choice == '2':
            author = input("Enter the author's name"
                           " (just hit enter to go back): ")
            if author == "":
                continue
            else:
                search_books_by_author(author)

        elif choice == '3':
            genre = input("Enter the genre"
                          " (just hit enter to go back): ")
            if genre == "":
                continue
            else:
                search_books_by_genre(genre)

        elif choice == 'q':
            time.sleep(1)
        else:
            print("Invalid choice. Please enter a number")
            time.sleep(2)


# define the display_books function
def display_books():
    """
    Display books in the database, 6 books per page with navigation controls
    """
    while True:
        print("\033[2J\033[H")
        cprint("BOOK INVENTORY", 'green', attrs=['bold'])

        # get all the records from the sheet
        records = SHEET.get_all_records()

        # format data for tabulate
        data = [[record['Title'],
                 record['Author'],
                 record['Year Published'] or '',
                 record['Genre']]
                for record in records]

        # display records in pages of 6
        page = 1
        total_pages = (len(records) + 5) // 6
        while page <= total_pages:
            start = (page - 1) * 6
            end = start + 6
            print("\033[2J\033[H")
            cprint("BOOK INVENTORY", 'green', attrs=['bold'])
            print(tabulate(data[start:end],
                           headers=['Title', 'Author', 'Year', 'Genre'],
                           tablefmt='fancy_grid',
                           maxcolwidths=20
                           ))
            print(f"Page {page} of {total_pages}")
            choices = [
                List('action',
                     message="Choose an action",
                     choices=['Next page', 'Previous page', 'Back'])
            ]
            answer = prompt(choices, theme=GreenPassion())
            if answer['action'] == 'Next page':
                if page < total_pages:
                    page += 1
            elif answer['action'] == 'Previous page':
                if page > 1:
                    page -= 1
            elif answer['action'] == 'Back':
                return


# define the main function
def main():
    """
    Main function runs at start.
    The function takes user input and calls corresponding sub-functions.
    The function exits the program when the user chooses to exit.
    """
    # Ask the user if they want to login or create a new user
    while True:
        print("\033[2J\033[H")
        login_choice = prompt([
            List('login_choice',
                 message="Choose an option:",
                 choices=['Login',
                          'Create User',
                          'Quit']),
        ], theme=GreenPassion())['login_choice']

        if login_choice == 'Quit':
            return
        elif login_choice == 'Create User':
            create_user()
        elif login_choice == 'Login':
            # Prompt the user to login until a
            # valid username and password is entered
            while True:
                result = login()
                if result is True:
                    break
                elif result == "Q":
                    break
                else:
                    print("Invalid username or password. Please try again.")
            if result is True:
                break

    while True:
        choice = main_menu()
        if choice == '1':
            add_book_menu()
        elif choice == '2':
            remove_book()
        elif choice == '3':
            update_book()
        elif choice == '4':
            search_choice()
        elif choice == '5':
            display_books()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number")


# ASCII title screen
print("\033[2J\033[H")
cprint(r'''
                        .-~~~~~~~~~-._       _.-~~~~~~~~~-.
                    __.'              ~.   .~              `.__
                .'//                  \./                  \\`.
                .'//                     |                     \\`.
            .'// .-~"""""""~~~~-._     |     _,-~~~~"""""""~-. \\`.
            .'//.-"                 `-.  |  .-'                 "-.\\`.
        .'//______.============-..   \ | /   ..-============.______\\`.
        .'______________________________\|/______________________________`.
                ______             _    _    _
                | ___ \           | |  | |  | |
                | |_/ / ___   ___ | | _| |  | | ___  _ __ _ __ ___
                | ___ \/ _ \ / _ \| |/ | |/\| |/ _ \| '__| '_ ` _ \
                | |_/ | (_) | (_) |   <\  /\  | (_) | |  | | | | | |
                \____/ \___/ \___/|_|\_\\/  \/ \___/|_|  |_| |_| |_|
''', 'green')

input("Press Enter to continue...".center(80))
print("\033[2J\033[H")

# call main function

main()
