from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver


def _parse_gundem(html: str, selector: str) -> List[Dict[str, str]]:
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
        results.append({"title": title, "url": full_url, "count": count})

    return results


def get_gundem(
        headline: Optional[str] = None,
        sync_driver: str = "uc",
        headless: bool = False,
        selector_override: Optional[str] = None,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None
) -> List[Dict[str, str]]:

    selector = selector_override or SELECTORS["gundem"]["container"]
    wait_for_class = SELECTORS["gundem"]["wait_for_class"]
    website = SELECTORS["website"]

    if headline:
        website = f"{website}/basliklar/kanal/{headline}"

    try:
        browser = get_browser_driver(
            name=sync_driver, headless=headless, binary_location=binary_location, version_main=version_main
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize browser driver: {e}")

    try:
        html = browser.get_html(website, wait_for_class=wait_for_class)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        browser.quit()

    results = _parse_gundem(html, selector)
    return results


async def get_gundem_async(
        headline: Optional[str] = None,
        async_driver: str = "uc",
        headless: bool = False,
        selector_override: Optional[str] = None,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None
) -> List[Dict[str, str]]:

    selector = selector_override or SELECTORS["gundem"]["container"]
    wait_for_class = SELECTORS["gundem"]["wait_for_class"]
    website = SELECTORS["website"]

    if headline:
        website = f"{website}/basliklar/kanal/{headline}"

    try:
        browser = get_browser_driver(
            name=async_driver, headless=headless, binary_location=binary_location, version_main=version_main
        )
        html = await browser.get_html_async(website, wait_for_class=wait_for_class)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        browser.quit()

    results = _parse_gundem(html, selector)
    return results
