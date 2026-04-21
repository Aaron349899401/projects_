# main.py — wire everything up
from crawler import crawl
from indexer import build_index, search, save_index, load_index

# Crawl
pages = crawl("https://en.wikipedia.org/wiki/Python_(programming_language)", max_pages=30)

# Index
index, doc_info = build_index(pages)
save_index(index, doc_info)

# Search
index, doc_info = load_index()
results = search("fast interpreted language", index, doc_info)

for r in results:
    print(f"\n[{r['score']}] {r['title']}")
    print(f"  {r['url']}")
    print(f"  {r['snippet'][:120]}...")