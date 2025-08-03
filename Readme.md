# eksiminer

**eksiminer** is a Python package for scraping entries, topics, authors, and daily highlights from [Ekşi Sözlük](https://eksisozluk.com), one of Turkey's most popular social platforms. It provides a simple interface to extract trending topics, DEBE (Dünün En Beğenilen Entry'leri), individual entries, and user-specific content.

> ⚠️ This package requires a Chromium-based browser driver. Provide the path using the `binary_location` parameter.

---

## 📦 Installation

```bash
pip install eksiminer
```

#### Usage Examples

**Get Gündem (Trending Topics)**

```python
from eksiminer import get_gundem

results = get_gundem(binary_location=binary_location)

print(len(results))

results = get_gundem(binary_location=binary_location, headline="siyaset")

print(len(results))
```

Returns a list of trending topic titles on Ekşi Sözlük.

**Scrape Entries from a Topic**

```python
from eksiminer import TopicScraper

topic = "Ekrem İmamoğlu"

scraper = TopicScraper(binary_location=binary_location)

results = scraper.scrape(topic=topic, max_page_limit=3, reverse=True)

print(len(results))
```

Scrapes entries from a given topic. You can limit the number of pages and choose reverse chronological order.

**Get DEBE List (Best of Yesterday)**

```python
from eksiminer import get_debe_list

results = get_debe_list(binary_location=binary_location)

print(len(results))
```

Returns a list of DEBE topics (most liked entries of the previous day).

**Get Specific Entry from URL**

```python
from eksiminer import get_entry_from_url

url = "https://eksisozluk.com/entry/173974269"

result = get_entry_from_url(url=url, binary_location=binary_location)

print(result)
```

Fetches a specific entry given its URL.

**Scrape Entries by Author**

```python
from eksiminer import AuthorScraper

author = "seven years in tibet"

scraper = AuthorScraper(binary_location=binary_location)

entries = scraper.scrape(author=author, number_endless_scroll=3)

print(len(entries))
```

**Scrate Entries by URLs**

```python
from eksiminer import TopicUrlService

urls = [
    "https://eksisozluk.com/29-temmuz-2025-ozgur-ozel-komisyon-aciklamasi--8009885?a=popular",
    "https://eksisozluk.com/arabada-ideal-klima-derecesi--6157779?a=popular"
]

scraper = TopicUrlService(binary_location=binary_location)

entries = scraper.scrape(urls=urls, max_page_limit=2, reverse=True)

print(len(entries))
```

Scrapes entries written by a specific author. You can set how many times to click "load more" with click_threshold.

## Licence

MIT License.

## Contributions

Feel free to open issues or submit pull requests. Contributions are welcome!
