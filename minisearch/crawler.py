import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin, urlparse
import time

def crawl(seed_url, max_pages=50):
    frontier = deque([seed_url])
    visited  = set()
    pages    = {}

    base_domain = urlparse(seed_url).netloc

    while frontier and len(visited) < max_pages:
        url = frontier.popleft()

        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=5, headers={
                "User-Agent": "MiniSearchBot/1.0"
            })
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"  Failed: {url} — {e}")
            visited.add(url)
            continue

        visited.add(url)
        print(f"[{len(visited)}/{max_pages}] Crawled: {url}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Grab article body for Wikipedia, full page for everything else
        content = soup.find("div", {"id": "mw-content-text"})
        if not content:
            content = soup

        # Strip noise
        for tag in content(["script", "style", "nav", "footer", "table"]):
            tag.decompose()
        for tag in content.find_all(class_="mw-editsection"):
            tag.decompose()

        text = content.get_text(separator=" ", strip=True)
        pages[url] = text

        # Extract and queue links from the full soup (not just content)
        for a_tag in soup.find_all("a", href=True):
            href = urljoin(url, a_tag["href"])
            parsed = urlparse(href)

            href = parsed._replace(fragment="").geturl()
            parsed = urlparse(href)

            if (parsed.netloc == base_domain
                    and parsed.scheme in ("http", "https")
                    and href not in visited):
                frontier.append(href)

        time.sleep(0.5)

    print(f"\nDone. Crawled {len(pages)} pages.")
    return pages


if __name__ == "__main__":
    results = crawl("https://en.wikipedia.org/wiki/Python_(programming_language)", max_pages=30)
    for url, text in results.items():
        print(f"\n--- {url} ---")
        print(text[:300])