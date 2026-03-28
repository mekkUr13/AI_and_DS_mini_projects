import pandas as pd # optional
import csv # optional
import os
import sys
import time
from whoosh.index import create_in
from whoosh.fields import Schema, ID, TEXT, DATETIME, KEYWORD, STORED
from datetime import datetime

'''
Authors:
- Bartosz Stoklosa
- Baranyi Sándor
'''

schema = Schema(
    id = ID(stored=True, unique=True), # Unique identifier of the article.
    url = ID(stored=True), # Link to the original article.
    title = TEXT(stored=True),
    content = TEXT(stored=False),
    category_level_1 = KEYWORD(commas=True, lowercase=True, stored=True),
    source = TEXT(stored=True),
    date = DATETIME(stored=True),
    published_utc = DATETIME(stored=True),
    collection_utc = DATETIME(stored=True),
    category_level_2 = KEYWORD(commas=True, lowercase=True, stored=True), # Second level category of Media Topic NewsCodes's taxonomy.
)


if __name__ == "__main__":
    """ python Indexer.py path_to_dataset index_directory """

    path_to_dataset = sys.argv[1] # Path to the dataset.
    index_dir = sys.argv[2] # Index directory.

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    ix = create_in(index_dir, schema)
    writer = ix.writer()
    cnt = 0
    time_start = time.time()

    category_counts = {}
    with open(path_to_dataset, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                news_id = row["id"]
                title = row["title"]
                content = row["content"]
                cat1 = row["category_level_1"]
                cat2 = row["category_level_2"]
                source = row["source"]
                date_str = row["date"]
                published_utc_ts = int(row["published_utc"])
                collection_utc_ts = int(row["collection_utc"])

                # Convert date string to datetime
                date_obj = datetime.fromisoformat(date_str)
                published_utc_dt = datetime.fromtimestamp(published_utc_ts)
                collection_utc_dt = datetime.fromtimestamp(collection_utc_ts)

                writer.add_document(
                    id=news_id,
                    title=title,
                    content=content,
                    category_level_1=cat1,
                    category_level_2=cat2,
                    source=source,
                    date=date_obj,
                    published_utc=published_utc_dt,
                    collection_utc=collection_utc_dt,
                    url=row["url"]
                )

                category_counts[cat1] = category_counts.get(cat1, 0) + 1
                cnt += 1
            except Exception as e:
                print(f"Error processing row {row['id']}: {e}")
                continue

    print("=" * 30)
    for cat, total in sorted(category_counts.items()):
        print(f'Category: "{cat}", total news: {total}')
    print("=" * 30)
    print(f"Total of indexed news: {cnt}")
    print("Writing the index...")


    #IT IMPORTANT TO DO THE COMMIT TO PERSIST CHANGES
    writer.commit()
    ttime = time.time() - time_start
    print("Total time: %.1fs. (%.1fm.)" % (ttime, ttime / 60))
    print("=" * 30)


""" OUTPUT FOR: python LNR_indexer_solution1.py MN-DS-news-classification.csv ./ind
==============================
Category: "arts, culture, entertainment and media", total news: 300
Category: "conflict, war and peace", total news: 800
Category: "crime, law and justice", total news: 500
Category: "disaster, accident and emergency incident", total news: 500
Category: "economy, business and finance", total news: 400
Category: "education", total news: 607
Category: "environment", total news: 600
Category: "health", total news: 700
Category: "human interest", total news: 600
Category: "labour", total news: 703
Category: "lifestyle and leisure", total news: 300
Category: "politics", total news: 900
Category: "religion and belief", total news: 800
Category: "science and technology", total news: 800
Category: "society", total news: 1100
Category: "sport", total news: 907
Category: "weather", total news: 400
==============================
Total of indexed news: 10917
Writing the index...
Total time: 76.1s. (1.3m.)
==============================
"""