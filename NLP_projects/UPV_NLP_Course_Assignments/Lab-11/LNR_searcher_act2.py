from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, OrGroup
import argparse


'''
Authors:
- Bartosz Stoklosa
- Baranyi Sándor
'''

def make_query(index, query, ext=False, default="content"):
    print()
    ix = index
    parser = MultifieldParser(["title", "content"], schema=ix.schema, group=OrGroup)
    parsed_query = parser.parse(query.lower())  # lowercase helps stem match

    with ix.searcher() as searcher:
        results = searcher.search(parsed_query, limit=None)
        print(f"Query: {parsed_query}\n")

        if ext:
            if results:
                doc = results[0]
                print(f"Date: {doc.get('date')}")
                print(f"Title: {doc.get('title')}")
                print(f"Source: {doc.get('source')}")
                print(f"Collection: {doc.get('collection_utc')}")
                print(f"Published: {doc.get('published_utc')}")
                print(f"Category_level_1: {doc.get('category_level_1')}")
                print(f"Category_level_2: {doc.get('category_level_2')}")
                print(f"Url: {doc.get('url')}")
            else:
                print("No results found.")
        else:
            for r in results:
                print(f"-> ({r['date']}) {r['title']}")

        print("=" * 20)
        print(f"{len(results)} results")


def main_search(index, query=None, extend=False, dfield="content"):
    index = open_dir(index)
    if query is not None: make_query(index, query, extend, dfield)
    else:
        while True:
            #IF NOT QUERY IS GIVEN AS INPUT, REQUEST A QUERY
            query = input("Enter a query:")
            if len(query) == 0: break
            make_query(index, u''+query, extend, dfield)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("index_dir", help="path to the index directory.")
    
    parser.add_argument("-q", "--query", help="query to do a search from the command line.")
    
    parser.add_argument("-e", "--extend", action="store_true", default=False,
        help="show only the first result but in an extended form.")
    
    args = parser.parse_args()

    main_search(index=args.index_dir, query=args.query, extend=args.extend)