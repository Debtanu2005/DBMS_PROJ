from src.search_books.by_author_or_name import BookSearch

def demo_search():
    book_search = BookSearch()
    results = book_search.search("os")
    print(results)
if __name__ == "__main__":
    demo_search()