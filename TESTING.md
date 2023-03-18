# Book-Worm Manual Test Cases

## Test Case 1: Valid user input for adding a book manually

Test Steps:

1. Select "Add book" from the menu
2. Enter valid book details (e.g. "The Great Gatsby" for Title, "F. Scott Fitzgerald" for Author, "1925" for Year, and "Fiction" for Genre)
3. Press Enter

Expected Output:

- The book should be added to the library
- The message "Book added successfully!" should be displayed
- The program should prompt the user whether they want to add another book or return to the main menu

## Test Case 2: Invalid user input for adding a book manually

Test Steps:

1. Select "Add book" from the menu
2. Enter invalid book details (e.g. " " for Title, "abcd" for Year)
3. Press Enter

Expected Output:

- The message "Invalid {field}. Minimum 2 characters, alphanumeric." should be displayed
- The program should prompt the user to try again

## Test Case 3: Valid user input for adding a book by ISBN

Test Steps:

1. Select "Add book by ISBN" from the menu
2. Enter a valid ISBN (e.g. "9780743273565" for "The Great Gatsby" by F. Scott Fitzgerald)
3. Press Enter

Expected Output:

- The book details should be retrieved from the Google Books API
- The retrieved book details should be displayed to the user
- The program should prompt the user to confirm whether they want to add the book or not
- If the user confirms, the book should be added to the library
- The message "Book added successfully!" should be displayed
- The program should prompt the user whether they want to add another book or return to the main menu

## Test Case 4: Invalid user input for adding a book by ISBN

Test Steps:

1. Select "Add book by ISBN" from the menu
2. Enter an invalid ISBN (e.g. "1234567890123")
3. Press Enter

Expected Output:

- The message "Invalid ISBN. Please try again." should be displayed
- The program should prompt the user to try again

## Test Case 5: Valid user input for removing a book by title

Test Steps:

1. Select "Remove by title" from the menu
2. Enter the title of an existing book in the library
3. Press Enter

Expected Output:

- The book should be removed from the library
- The message "Book removed successfully!" should be displayed
- The program should prompt the user whether they want to remove another book or return to the main menu

## Test Case 6: Invalid user input for removing a book by title

Test Steps:

1. Select "Remove by title" from the menu
2. Enter the title of a non-existing book in the library
3. Press Enter

Expected Output:

- The message "The book is not in the database. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 7: Valid user input for removing a book by ISBN

Test Steps:

1. Select "Remove by ISBN" from the menu
2. Enter the ISBN of an existing book in the library
3. Press Enter

Expected Output:

- The book should be removed from the library
- The message "Book removed successfully!" should be displayed
- The program should prompt the user whether they want to remove another book or return to the main menu

## Test Case 8: Invalid user input for removing a book by ISBN

Test Steps:

1. Select "Remove by ISBN" from the menu
2. Enter an invalid ISBN (e.g. "1234")
3. Press Enter

Expected Output:

- The message "Invalid ISBN. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 9: Book not found for removing a book

Test Steps:

1. Select "Remove by title" from the menu
2. Enter the title of a book that does not exist in the library
3. Press Enter

Expected Output:

- The message "The book is not in the database. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 10: Valid user input for updating a book

Test Steps:

1. Select "Update book" from the menu
2. Enter the title of an existing book in the library
3. Select the field to update from the list (title, author, year, genre, ISBN)
4. Enter the new value for the selected field
5. Press Enter

Expected Output:

- The book details should be updated with the new value
- The message "Book updated successfully!" should be displayed
- The program should prompt the user whether they want to update another book or return to the main menu

## Test Case 11: Invalid user input for updating a book

Test Steps:

1. Select "Update book" from the menu
2. Enter the title of a non-existing book in the library
3. Select the field to update from the list (title, author, year, genre, ISBN)
4. Enter the new value for the selected field
5. Press Enter

Expected Output:

- The message "The book is not in the database. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 12: Valid user input for searching a book by title

Test Steps:

1. Select "Search by title" from the menu
2. Enter the title of an existing book in the library
3. Press Enter

Expected Output:

- The book details (title, author, year, genre, ISBN) should be displayed
- The program should prompt the user whether they want to search for another book or return to the main menu

## Test Case 13: Invalid user input for searching a book by title

Test Steps:

1. Select "Search by title" from the menu
2. Enter the title of a non-existing book in the library
3. Press Enter

Expected Output:

- The message "The book is not in the database. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 15: Valid user input for searching books by author

Test Steps:

1. Select "Search by author" from the menu
2. Enter the name of an author with an existing book in the library
3. Press Enter

Expected Output:

- The book(s) with matching author should be displayed with their details (title, author, year, genre)
- The program should prompt the user whether they want to search for another book or return to the main menu

## Test Case 16: Invalid user input for searching books by author

Test Steps:

1. Select "Search by author" from the menu
2. Enter a non-existing author in the library
3. Press Enter

Expected Output:

- The message "No books found with that author. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 17: Valid user input for searching books by genre

Test Steps:

1. Select "Search by genre" from the menu
2. Enter the name of an existing genre in the library
3. Press Enter

Expected Output:

- The book(s) with matching genre should be displayed with their details (title, author, year, genre)
- The program should prompt the user whether they want to search for another book or return to the main menu

## Test Case 18: Invalid user input for searching books by genre

Test Steps:

1. Select "Search by genre" from the menu
2. Enter a non-existing genre in the library
3. Press Enter

Expected Output:

- The message "No books found with that genre. Please try again." should be displayed
- The program should prompt the user to try again or return to the main menu

## Test Case 19: Valid user input for viewing all books

Test Steps:

1. Select "View all books" from the menu
2. Press Enter

Expected Output:

- All books in the library should be displayed with their details (title, author, year, genre)
- The program should prompt the user whether they want to return to the main menu

## Test Case 20: Valid user input for quitting the program

Test Steps:

1. Select "Quit" from the main menu
2. Press Enter

Expected Output:

- The program should terminate without any errors.
