# import required libraries
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from termcolor import cprint
from inquirer import prompt, List
from inquirer.themes import GreenPassion
from tabulate import tabulate

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


# define add_book_isbn function
def add_book_isbn():
    """
    Look up book details using an ISBN and add the book to the database
    """
    while True:
        print("\033[2J\033[H")
        print("LOOK UP BOOK BY ISBN\n")
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
            print(f"{title} added successfully!")
            time.sleep(2)
            return

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
    print(f"{'Title':<40} {'Author':<25} {'Genre':<20} {'Year':<10}")
    print("-" * 80)

    for book in matching_books:
        print(f"{book['title']:<40} {book['author']:<25} {book['genre']:<20}"
              f"{book['year']:<10}")
    input("Press enter to exit")


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
            print("No books found with that search term.")
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
    print("What would you like to search for:")
    print("1. Search for books by author")
    print("2. Search for books by genre")
    print("3. Exit")

    choice = input("Enter your choice: ")
    return choice


def search_choice():
    """
    Handles the user's search choice.
    """
    while True:
        choice = search_menu()

        if choice == '1':
            author = input("Enter the author's name"
                           " (just hit enter to go back): ")
            search_books_by_author(author)

        elif choice == '2':
            genre = input("Enter the genre"
                          " (just hit enter to go back): ")
            search_books_by_genre(genre)

        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter a number")
            time.sleep(2)


# define the display_books function
def display_books():
    """
    Display books in the database, 10 books per page with navigation controls
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

        # display records in pages of 10
        page = 1
        total_pages = (len(records) + 9) // 10
        while page <= total_pages:
            start = (page - 1) * 10
            end = start + 10
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
print(r'''
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
        \____/ \___/ \___/|_|\_\\\/  \/ \___/|_|  |_| |_| |_|

''')

input("Press Enter to continue...")
print("\033[2J\033[H")


# call main function

main()
