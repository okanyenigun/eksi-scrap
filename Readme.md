# eksiminer

A Python package for scraping [Ekşi Sözlük](https://eksisozluk.com) - trending topics, entries, authors, and DEBE lists.

## Installation

```bash
pip install eksiminer
```

## Quick Start

```python
from eksiminer import get_trending_topics

results = get_trending_topics(headless=True)
print(results[0])
```

## Usage

**Get Trending Topics**

```python
from eksiminer import get_trending_topics

# All trending topics
results = get_trending_topics(headless=True)

# Specific channel (spor, siyaset, iliskiler, etc.)
results = get_trending_topics(channel="siyaset", headless=True)
```

**Get Topic Entries**

```python
from eksiminer import get_topic_entries

# Single topic
results = get_topic_entries(
    topic="yapay zeka",
    max_page_limit=2,
    headless=True
)

# Multiple topics
results = get_topic_entries(
    topic=["topic1", "topic2"],
    max_page_limit=2,
    headless=True
)
```

**Get DEBE List**

```python
from eksiminer import get_debe_topics_list

results = get_debe_topics_list(headless=True)
```

**Get Entry by URL**

```python
from eksiminer import get_entry_by_url

entry = get_entry_by_url("https://eksisozluk.com/entry/123456", headless=True)
```

**Get Author Entries**

```python
from eksiminer import get_author_entries

entries = get_author_entries(
    author="username",
    number_endless_scroll=10,
    headless=True
)
```

**Reuse Driver (Faster)**

```python
from eksiminer import UCDriverClient, get_trending_topics, get_debe_topics_list

driver = UCDriverClient(headless=True)

trending = get_trending_topics(driver=driver)
debe = get_debe_topics_list(driver=driver)

driver.close()
```

## LangChain Integration

```bash
pip install eksiminer langchain langchain-openai
```

```python
from eksiminer.extensions.tools.langchain import (
    get_trending_topics_tool,
    get_topic_entries_tool,
    get_debe_topics_list_tool,
    get_entry_by_url_tool,
    get_author_entries_tool
)
```

## Documentation

- [tutorial.ipynb](tutorial.ipynb) - Interactive examples

## License

MIT License
