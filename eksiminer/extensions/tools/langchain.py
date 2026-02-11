from typing import List, Dict, Union, Optional
from ...services.author import get_author_entries
from ...services.debe import get_debe_topics_list
from ...services.topic import get_topic_entries
from ...services.trending import get_trending_topics
from ...services.url import get_entry_by_url


def _get_tool_decorator():
    try:
        from langchain_core.tools import tool

        return tool
    except ImportError:
        raise ImportError(
            "Please install langchain to use eksiminer's langchain tools: pip install langchain"
        )


@(_get_tool_decorator())
def get_author_entries_tool(
    author: str, number_endless_scroll: int = 10
) -> List[Dict[str, str]]:
    """
    This gets entries made by a specific author on Ekşi Sözlük.

    Args:
        author (str): The author's username.
        number_endless_scroll (int, optional): The number of times to perform endless scrolling. Defaults to 10.

    Returns:
        List[Dict[str, str]]: A list of entries made by the author.
        Example:
        [
            {
                'title': 'fenerbahçe',
                'content': "1907. entry'm senin adına olsun istedim. “bütün duyguları anlatmaya yetecek kadar kelime yoktur, gerek de yoktur” der cengiz aytmatov . onun yerine bu sevdaya nasıl bulaştığımıza dair bir video bırakayım. çünkü bazen ufak bir enstantane, sayfalarca yazı yazmaktan daha iyi açıklar durumu: link",
                'date': '02.08.2024 19:19'
            },
            ...
        ]
    """
    return get_author_entries(
        author=author,
        number_endless_scroll=number_endless_scroll,
    )


@(_get_tool_decorator())
def get_debe_topics_list_tool() -> List[Dict[str, str]]:
    """
    Get a list of debe (most liked entries of yesterday, dünün en beğenilen entry'leri in turkish) entries.

    Args:
        None

    Raises:
        e: _any exception that occurs during scraping_

    Returns:
        List[Dict[str, str]]: A list of debe entries.
        Example:
        [
            {
                'title': "esenyurt'ta yayaları durdurup haraç kesen çete",
                'url': 'https://eksisozluk.com/entry/177149240?debe=true'
            },
            ...
        ]
    """
    return get_debe_topics_list()


@(_get_tool_decorator())
def get_topic_entries_tool(
    topic: Union[str, List[str]],
    max_page_limit: Optional[int] = None,
    reverse: bool = False,
    verbose: bool = False,
) -> Dict[str, List[Dict[str, str]]]:
    """
    Scrap entries for a given topic or list of topics in Ekşi Sözlük.

    Args:
        topic (Union[str, List[str]]): The topic or list of topics to scrape.
        max_page_limit (Optional[int], optional): The maximum number of pages to scrape. Defaults to None.
        reverse (bool, optional): Whether to scrape pages in reverse order. Defaults to False.
        verbose (bool, optional): Whether to enable verbose output. Defaults to False.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary mapping topics to their scraped entries.
        Example:
        {
            "example_topic": [
                {
                    'content': 'hobileri arasında yeliz kod adlı akpli ahmet hamdi çamlı dan alıntı yapmak bulunan, alıntı yapmayı çok seven şahıs. kendisinin diplomasının sahte olduğu gibi, karısının da yüksek lisans diploması çalıntı çıkmış. karı-koca karakterleri uyumlu bir evlilik yapmışlar. di\'nin diploması çalıntıdır bir tarafta sahte diplomalı futbolcular, diğer tarafta sahte diplomalı müteahhitler. neden bu iki rezil şıktan birini seçiyoruz diye sorgulamak yerine, adice, ahlaksızca kendisini savunacak yaratıklar bulunacaktır. gerizekalı şerefsizlerden duyabileceğiniz argümanlar: "bizim tarafın sahte diplomalılarını desteklemiyorsanız, karşı tarafa çalışıyorsunuz, gerçek atatürkçü, rozet takar, dövme yaptırır ve oklu partinin sahte diplomalılarını destekler..."',
                    'author': 'hiperaktf c',
                    'date': '29.07.2025 13:32 ~ 15:51',
                    'topic': 'yeliz kod adlı akpli ahmet hamdi çamlı',
                },
                ...
            ],
            ...
        }
    """
    return get_topic_entries(
        topic=topic, max_page_limit=max_page_limit, reverse=reverse, verbose=verbose
    )


@(_get_tool_decorator())
def get_trending_topics_tool(channel: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Get the current trending topics from the Ekşi Sözlük website.

    Args:
        channel (Optional[str]): Specific channel to filter trending topics. None for general, or spor, iliskiler, yasam, kripto, siyaset, seyahat, tv, haber, bilim, edebiyat for sub-channels.

    Returns:
        List[Dict[str, str]]: The list of trending topics.
        Example:
        [
            {
                'title': '29 temmuz 2025 özgür özel komisyon açıklaması',
                'url': 'https://eksisozluk.com/29-temmuz-2025-ozgur-ozel-komisyon-aciklamasi--8009885?a=popular',
                'count': '270'
            },
            ...
        ]
    """
    return get_trending_topics(channel=channel)


@(_get_tool_decorator())
def get_entry_by_url_tool(url: str) -> Dict[str, str]:
    """
    Get entry details from a URL.

    Args:
        url (str): The URL of the entry from Ekşi Sözlük.

    Returns:
        Dict[str, str]: A dictionary containing entry details.
        Example:
        {
            'content': "öcü gibi korkuyorlar senden başkanım! haklılar, korkmalılar! seni başkan yapacağız! unutmayacağız seni, çıkaracağız en kısa zamanda. ama bir söz ver bize, başkan seçilince beştepe'ye geçme. çankaya köşkü yakışır sana.",
            'author': 'sequasa',
            'date': '25.03.2025 23:11',
            'title': 'ekrem imamoğlu'
        }
    """
    return get_entry_by_url(url=url)
