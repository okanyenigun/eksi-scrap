from .services.trending import get_trending_topics
from .services.topic import get_topic_entries
from .services.debe import get_debe_topics_list
from .services.url import get_entry_by_url
from .services.author import get_author_entries
from .core.drivers.uc_client import UCDriverClient


__all__ = [
    "UCDriverClient",
    "get_trending_topics",
    "get_topic_entries",
    "get_debe_topics_list",
    "get_entry_by_url",
    "get_author_entries",
]


__version__ = "0.0.3"
