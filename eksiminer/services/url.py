from bs4 import BeautifulSoup
from typing import Dict, Optional
from .selectors import SELECTORS
from ..core.drivers.uc_client import UCDriverClient
from ..core.drivers.base_driver import DriverClient
from ..core.schemas import TopicBaseResponse


def get_entry_by_url(
    url: str,
    driver: Optional[DriverClient] = None,
    headless: bool = False,
    driver_path: Optional[str] = None,
    driver_version: Optional[int] = None,
) -> Dict[str, str]:
    """
    Get entry details from a URL.

    Args:
        url (str): The URL of the entry.
        driver (Optional[DriverClient], optional): _Pre-initialized browser driver client_. Defaults to None.
        headless (bool, optional): _Run browser in headless mode_. Defaults to False.
        driver_path (Optional[str], optional): _Path to the browser binary_. Defaults to None.
        driver_version (Optional[int], optional): _Version of the browser driver_. Defaults to None.

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
    driver_initialized = False

    content_class = SELECTORS["entry_from_url"]["content"]
    author_class = SELECTORS["entry_from_url"]["author"]
    date_class = SELECTORS["entry_from_url"]["date"]
    title_class = SELECTORS["entry_from_url"]["title"]

    if not driver:
        driver = UCDriverClient(
            headless=headless,
            binary_location=driver_path,
            version_main=driver_version,
        )
        driver_initialized = True

    driver.get(url, by="css selector", wait_for=content_class)
    driver.scroll_to_bottom()

    soup = BeautifulSoup(driver.page_source, "html.parser")

    content_div = soup.select_one(content_class)
    author_a = soup.select_one(author_class)
    date_a = soup.select_one(date_class)
    title_h1 = soup.select_one(title_class)

    record = TopicBaseResponse(
        title=title_h1.text.strip() if title_h1 else None,
        content=content_div.get_text(separator=" ", strip=True)
        if content_div
        else None,
        author=author_a.text.strip() if author_a else None,
        date=date_a.text.strip() if date_a else None,
    )

    if driver_initialized:
        driver.close()

    return record.model_dump()
