# Books, Books, Books

Web Programming with Python and JavaScript

## Project Description
Website that allows user to create login and submit reviews for books

## Files

### application.py
main python file, uses flask to create web routes

### import.py
CSV reader, turns books.csv into database 

### books.csv
List of available books

### requirements.txt
List of plugins required to run application.py

### layout.html
Basic layout that extends to all html files. Includes navigation bar

### index.html
Home Page   
route: `/`

### logoff.html
User logoff  
route: `/logoff`

### logon.html
User logon   
route: `/logon`

### profile.html
User profile  
route: `/profile`

### registration.html
User registration  
route: `/registration`

### search.html 
Book Search  
route: `/search`

### books.html
Searched book results  
route: `/books`

### book.html
Book page   
route: `/book/<int:book_id>/`  

`book_id` is the id in database `books `  
User can view book info, read and submit reviews  

###create.sql
Database creation  
Tables: books, login, reviews


## API
### route: `/api/<book_isbn>`    
JSON file for book  
book_isbn is the book's isbn #  
 
 
