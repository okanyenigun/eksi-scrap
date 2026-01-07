
from ...services.topic_url_service import TopicUrlService
from ...services.util_service import get_entry_from_url
from ...services.debe_service import get_debe_list
from ...services.author_service import AuthorScraper
from ...services.topic_service import TopicScraper
from ...services.gundem_service import get_gundem
from typing import List, Dict, Literal, Optional


def _get_tool_decorator():
    try:
        from langchain_core.tools import tool
        return tool
    except ImportError:
        raise ImportError(
            "Please install langchain to use eksiminer's langchain tools: pip install langchain")


@(_get_tool_decorator())
def get_popular_topic_titles(
    binary_location: str,
    channel: Optional[Literal["spor", "iliskiler", "yasam", "kripto",
                              "siyaset", "seyahat", "tv", "haber", "bilim", "edebiyat"]] = None,
) -> List[Dict[str, str]]:
    """
    Gets the current popular topics of the day.

    Args:
        binary_location (str): The file path to the binary executable.
        channel (Optional[Literal[spor, iliskiler, yasam, kripto, siyaset, seyahat, tv, haber, bilim, edebiyat]], optional):
            The specific channel to get popular topics from. Defaults to None. Options include 'spor', 'iliskiler', 'yasam', 'kripto', 'siyaset', 'seyahat', 'tv', 'haber', 'bilim', 'edebiyat'. If None, fetches the most popular topics in general.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing popular topics.
    Example:
    [
        {
            'title': "3 ocak 2026 abd'nin maduro ve eşini kaçırması",
            'url': 'https://eksisozluk.com/3-ocak-2026-abdnin-maduro-ve-esini-kacirmasi--8060447?a=popular',
            'count': '527'
        },
        ...
    ]
    """

    return get_gundem(binary_location=binary_location, channel=channel)


@(_get_tool_decorator())
def get_entries_by_topic(
    binary_location: str,
    topic: str,
    max_page_limit: int = 3,
    reverse: bool = True
) -> List[Dict[str, str]]:
    """
    Gets entries for a given topic.
    Args:
        binary_location (str): The file path to the binary executable.
        topic (str): The topic to get entries for.
        max_page_limit (int, optional): The maximum number of pages to scrape. Defaults to 3.
        reverse (bool, optional): Whether to reverse the order of entries. Defaults to True.

    Returns:
        List[Dict[str, str]]:
    Example:
    [
        {
            'topic': 'Ekrem İmamoğlu',
            'content': '30 yıl önce çekilmiş filme klişe diyen adamdan daha mantıklı hareket etmiş halktır. arkadaşım klişe ilk yapılana denmiyor sonradan yapılanlara deniyor.',
            'author': 'hulloled',
            'date': '01.09.2014 13:52'
        },
        ...
    ]
    """
    scraper = TopicScraper(binary_location=binary_location)
    entries = scraper.scrape(
        topic=topic, max_page_limit=max_page_limit, reverse=reverse)
    return entries


@(_get_tool_decorator())
def get_debe(
    binary_location: str
) -> List[Dict[str, str]]:
    """
    Gets the list of most upvoted (debe) entries.

    Args:
        binary_location (str): The file path to the binary executable.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing debe entries.
    Example:
    [
        {
            'title': 'danimarka',
            'url': 'https://eksisozluk.com/entry/180956991?debe=true'
        },
        ...
    ]
    """
    entries = get_debe_list(binary_location=binary_location)
    return entries


@(_get_tool_decorator())
def get_entry_by_url(
    binary_location: str,
    url: str
) -> Dict[str, str]:
    """
    Gets a single entry by its URL.

    Args:
        binary_location (str): The file path to the binary executable.
        url (str): The URL of the entry to retrieve.

    Returns:
        Dict[str, str]: A dictionary containing the entry details.
    Example:
    {
        'topic': 'ekrem imamoğlu', 
        'content': "öcü gibi korkuyorlar senden başkanım! haklılar, korkmalılar! seni başkan yapacağız! unutmayacağız seni, çıkaracağız en kısa zamanda. ama bir söz ver bize, başkan seçilince beştepe'ye geçme. çankaya köşkü yakışır sana.", 
        'author': 'sequasa', 
        'date': '25.03.2025 23:11'
    }
    """
    entry = get_entry_from_url(url=url, binary_location=binary_location)
    return entry


@(_get_tool_decorator())
def get_entries_by_author(
    binary_location: str,
    author: str,
    number_endless_scroll: int = 5
) -> List[Dict[str, str]]:
    """
    Gets entries for a given author.
    Args:
        binary_location (str): The file path to the binary executable.
        author (str): The author to get entries for.
        number_endless_scroll (int, optional): The number of times to scroll for more entries. Defaults to 5.

    Returns:
        List[Dict[str, str]]: 
    Example:
    [
        {
            'topic': 'fenerbahçe',
            'content': "1907. entry'm senin adına olsun istedim. “bütün duyguları anlatmaya yetecek kadar kelime yoktur, gerek de yoktur” der cengiz aytmatov . onun yerine bu sevdaya nasıl bulaştığımıza dair bir video bırakayım. çünkü bazen ufak bir enstantane, sayfalarca yazı yazmaktan daha iyi açıklar durumu: link",
            'author': 'seven years in tibet',
            'date': '02.08.2024 19:19'
        },
        ...
    ]
    """
    scraper = AuthorScraper(binary_location=binary_location)
    entries = scraper.scrape(
        author=author, number_endless_scroll=number_endless_scroll)

    return entries


@(_get_tool_decorator())
def get_topic_entries_by_url(
    binary_location: str,
    urls: List[str],
    max_page_limit: int = 3,
    reverse: bool = True
) -> List[Dict[str, str]]:
    """
    Gets topic entries by a list of topic URLs.

    Args:
        binary_location (str): The file path to the binary executable.
        urls (List[str]): a list of topic URLs to scrape entries from.
        max_page_limit (int, optional): The maximum number of pages to scrape. Defaults to 3.
        reverse (bool, optional): Whether to reverse the order of entries. Defaults to True.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing topic entries.
    Example:
    [
        {
            'topic': 'https://eksisozluk.com/29-temmuz-2025-ozgur-ozel-komisyon-aciklamasi--8009885', 
            'content': 'evet biz de nerede kalmıştık diyorduk. özgür özel zirvede bırakmış anlaşılan. üç aylık prime döneminden sonra jübilesini yaptı sanırım. god mode açmış, gençlerle ve halkla yakın temas kuran özgür out; kürtçü, kırmızı kartçı, kk dedesinin kurban olduğu özgür in! süreç denen saçmalığa asla destek vermiyorum ama madem destek vereceksin bari ekrem başkan konusunda şansını zorla bir meseleyi sıcak tut di mi ama? hem hiçbir şey alamıyor hem de destek veriyor. stratejik zeka bunun neresinde?', 
            'author': 'kececiazmi', 
            'date': '31.07.2025 03:45'
        },
        ...
    ]
    """
    service = TopicUrlService(binary_location=binary_location)
    entries = service.scrape(
        urls=urls, max_page_limit=max_page_limit, reverse=reverse)
    return entries
