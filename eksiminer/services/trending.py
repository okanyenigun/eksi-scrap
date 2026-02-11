from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.schemas import GundemResponse
from ..core.drivers.base_driver import DriverClient
from ..core.drivers.uc_client import UCDriverClient


def _parse_gundem(html: str, selector: str) -> List[GundemResponse]:
    website = SELECTORS["website"]

    soup = BeautifulSoup(html, "html.parser")
    links = soup.select(selector)

    results = []
    for a_tag in links:
        href = a_tag["href"]
        title = a_tag.get_text(strip=False)
        title_list = title.split(" ")
        if title_list[-1].isdigit():
            title = " ".join(title_list[:-1])
            count = title_list[-1]
        else:
            count = "0"
            title = " ".join(title_list)
        full_url = f"{website}{href}"
        results.append(GundemResponse(title=title, url=full_url, count=count))

    return results


def get_trending_topics(
    channel: Optional[str] = None,
    driver: Optional[DriverClient] = None,
    headless: bool = False,
    selector_class: Optional[str] = None,
    driver_path: Optional[str] = None,
    driver_version: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Get the current trending topics from the website.

    Args:
        channel (Optional[str]): Specific channel to filter trending topics. None for general, or spor, iliskiler, yasam, kripto, siyaset, seyahat, tv, haber, bilim, edebiyat for sub-channels.
        driver (Optional[DriverClient]): Pre-initialized browser driver client.
        headless (bool): Whether to run the browser in headless mode.
        selector_class (Optional[str]): CSS selector class for trending topics.
        driver_path (Optional[str]): Path to the browser binary. If None, auto-detection is attempted.
        driver_version (Optional[int]): Main version of the browser. If None, auto-detection is attempted.

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
    driver_initialized = False

    selector = selector_class or SELECTORS["gundem"]["container"]
    wait_for_class = SELECTORS["gundem"]["wait_for_class"]
    website = SELECTORS["website"]

    if channel:
        website = f"{website}/basliklar/kanal/{channel}"

    if not driver:
        driver = UCDriverClient(
            headless=headless,
            binary_location=driver_path,
            version_main=driver_version,
        )
        driver_initialized = True

    html = driver.get_html(website, wait_for=wait_for_class)

    if driver_initialized:
        driver.close()

    results = _parse_gundem(html, selector)
    results = [result.model_dump() for result in results]
    return results
