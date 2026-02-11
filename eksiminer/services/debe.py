from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.drivers.uc_client import UCDriverClient
from ..core.drivers.base_driver import DriverClient
from ..core.schemas import DebeResponse


def get_debe_topics_list(
    driver: Optional[DriverClient] = None,
    headless: bool = False,
    driver_path: Optional[str] = None,
    driver_version: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Get a list of debe (most liked entries of yesterday, dünün en beğenilen entry'leri in turkish) entries.

    Args:
        driver (Optional[DriverClient], optional): _Pre-initialized browser driver client_. Defaults to None.
        headless (bool, optional): _Run browser in headless mode_. Defaults to False.
        driver_path (Optional[str], optional): _Path to the browser binary_. Defaults to None.
        driver_version (Optional[int], optional): _Version of the browser driver_. Defaults to None.

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
    driver_initialized = False

    wait_for_class = SELECTORS["debe"]["wait_for_class"]
    container_class = SELECTORS["debe"]["container"]
    debe_website = SELECTORS["debe_website"]

    if not driver:
        driver = UCDriverClient(
            headless=headless,
            binary_location=driver_path,
            version_main=driver_version,
        )
        driver_initialized = True

    driver.get(
        url=debe_website,
        by="css selector",
        wait_for=wait_for_class,
    )
    driver.scroll_to_bottom()

    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        a_tags = soup.select(container_class)

        results = []
        for a_tag in a_tags:
            href = a_tag.get("href")
            title = a_tag.get_text(strip=True)
            full_url = f"https://eksisozluk.com{href}"
            results.append(DebeResponse(title=title, url=full_url))

        results = [entry.model_dump() for entry in results]

    except Exception as e:
        print(f"[ERROR] An error occurred while scraping debe list: {e}")
        raise e

    if driver_initialized:
        driver.close()

    return results
