from src.search_books.by_author_or_name import BookSearch
if __name__ == "__main__":
    query = input("Enter book name or author to search: ")
    book_search = BookSearch()
    results = book_search.search(query)

    print(results)
    
    # if results:
    #     print("Search Results:")
    #     for book in results:
    #         print(f"ID: {book[0]}, Name: {book[1]}, Author: {book[2]}, Available Copies: {book[3]}")
    # else:
    #     print("No books found matching the query.")