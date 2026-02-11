import time
from bs4 import BeautifulSoup
from typing import Optional, Tuple, List, Dict, Union
from .selectors import SELECTORS
from ..core.schemas import TopicBaseResponse
from ..core.drivers.uc_client import UCDriverClient
from ..core.drivers.base_driver import DriverClient


class TopicScraper:
    def __init__(
        self,
        driver: Optional[DriverClient] = None,
        verbose: bool = False,
        headless: bool = False,
        driver_path: Optional[str] = None,
        driver_version: Optional[int] = None,
    ):
        self.verbose = verbose
        self.headless = headless
        self.driver_path = driver_path
        self.driver_version = driver_version
        self.website = SELECTORS["website"]
        self.wait_for = SELECTORS["search"]["input"]
        self.input_element_id = SELECTORS["search"]["input"]
        self.button_element_selector = SELECTORS["search"]["button"]
        self.last_page_element_selector = SELECTORS["entry"]["total_page"]
        self.container_class = SELECTORS["entry"]["container"]
        self.author_class = SELECTORS["entry"]["author"]
        self.date_class = SELECTORS["entry"]["date"]
        self.content_class = SELECTORS["entry"]["content"]

        self.topic_url = None
        self.entries = []

        if not driver:
            self.driver = UCDriverClient(
                headless=self.headless,
                binary_location=self.driver_path,
                version_main=self.driver_version,
            )
            self.driver_initialized = True
        else:
            self.driver = driver
            self.driver_initialized = False

    def scrape(
        self, topic: str, max_page_limit: Optional[int] = None, reverse: bool = False
    ) -> List[Dict[str, str]]:
        self._open_search_page()
        self._submit_search(topic)
        _, page_range = self._get_total_pages(max_page_limit, reverse)
        self._scrape_pages(topic, page_range)

        if self.driver_initialized:
            self.driver.close()

        self.entries = [
            entry.model_dump() if hasattr(entry, "model_dump") else entry
            for entry in self.entries
        ]
        return self.entries

    def _open_search_page(self) -> None:
        self.driver.get(self.website, by="id", wait_for=self.wait_for)
        return

    def _submit_search(self, topic: str) -> None:
        search_box = self.driver.find_element("id", self.input_element_id)
        search_box.clear()
        search_box.send_keys(topic)

        submit_btn = self.driver.find_element(
            "css selector", self.button_element_selector
        )
        submit_btn.click()
        time.sleep(2)

        self.topic_url = self.driver.get_current_url()
        return

    def _get_total_pages(
        self, max_page_limit: Optional[int] = None, reverse: bool = False
    ) -> Tuple[int, range]:
        try:
            last_page_element = self.driver.find_element(
                "css selector", self.last_page_element_selector
            )
            total_pages = int(last_page_element.text)
        except Exception:
            total_pages = 1

        if max_page_limit is not None:
            page_count = min(max_page_limit, total_pages)
        else:
            page_count = total_pages

        if reverse:
            page_range = range(total_pages, total_pages - page_count, -1)
        else:
            page_range = range(1, page_count + 1)

        return page_count, page_range

    def _scrape_pages(self, topic: str, page_range: range) -> None:
        for page in page_range:
            page_entries = self._scrape_page_by_page_number(topic, page)
            self.entries.extend(page_entries)
            if self.verbose:
                print(f"[INFO] Scraped page {page}/{len(page_range)}")
        return

    def _scrape_page_by_page_number(
        self, topic: str, page_num: int
    ) -> List[TopicBaseResponse]:
        url = self.topic_url if page_num == 1 else f"{self.topic_url}?p={page_num}"
        self.driver.get(url, by="css selector", wait_for=self.container_class)

        self.driver.scroll_to_bottom()
        entries = self._extract_entries_from_page(topic)
        return entries

    def _extract_entries_from_page(self, topic: str) -> List[TopicBaseResponse]:
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        results = []

        entry_items = soup.select(self.container_class)
        for item in entry_items:
            content_div = item.select_one(self.content_class)
            author_a = item.select_one(self.author_class)
            date_a = item.select_one(self.date_class)
            entry = TopicBaseResponse(
                title=topic,
                content=content_div.get_text(separator=" ", strip=True)
                if content_div
                else None,
                author=author_a.text.strip() if author_a else None,
                date=date_a.text.strip() if date_a else None,
            )

            results.append(entry)
        return results


def get_topic_entries(
    topic: Union[str, List[str]],
    max_page_limit: Optional[int] = None,
    reverse: bool = False,
    driver: Optional[DriverClient] = None,
    headless: bool = False,
    driver_path: Optional[str] = None,
    driver_version: Optional[int] = None,
    verbose: bool = False,
) -> Dict[str, List[Dict[str, str]]]:
    """
    Scrap entries for a given topic or list of topics.

    Args:
        topic (Union[str, List[str]]): The topic or list of topics to scrape.
        max_page_limit (Optional[int], optional): The maximum number of pages to scrape. Defaults to None.
        reverse (bool, optional): Whether to scrape pages in reverse order. Defaults to False.
        driver (Optional[DriverClient], optional): The driver client to use. Defaults to None.
        headless (bool, optional): Whether to run the driver in headless mode. Defaults to False.
        driver_path (Optional[str], optional): The path to the driver executable. Defaults to None.
        driver_version (Optional[int], optional): The version of the driver to use. Defaults to None.
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
    entries = {}
    scraper = TopicScraper(
        driver=driver,
        verbose=verbose,
        headless=headless,
        driver_path=driver_path,
        driver_version=driver_version,
    )

    if isinstance(topic, str):
        entries[topic] = scraper.scrape(topic, max_page_limit, reverse)
    elif isinstance(topic, list):
        for t in topic:
            entries[t] = scraper.scrape(t, max_page_limit, reverse)
    else:
        raise ValueError("Topic must be a string or a list of strings.")
    return entries
