from bs4 import BeautifulSoup
from slugify import slugify
from typing import Optional, List, Dict
from .selectors import SELECTORS
from ..core.drivers.uc_client import UCDriverClient
from ..core.drivers.base_driver import DriverClient
from ..core.schemas import TopicBaseResponse


class AuthorScraper:
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
        self.load_more_class = SELECTORS["author"]["load_more"]
        self.topic_class = SELECTORS["author"]["topic"]
        self.title_class = SELECTORS["author"]["title"]
        self.content_class = SELECTORS["author"]["content"]
        self.date_class = SELECTORS["author"]["date"]

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
        self, author: str, number_endless_scroll: int = 10
    ) -> List[Dict[str, str]]:
        author_slug = slugify(author)
        url = f"https://eksisozluk.com/biri/{author_slug}"
        self.driver.get(url)
        self.driver.scroll_to_bottom()
        self._load_entries(number_endless_scroll)
        self.entries = self.parse_entries(author)
        self.entries = [entry.model_dump() for entry in self.entries]
        if self.driver_initialized:
            self.driver.close()
        return self.entries

    def _load_entries(self, number_endless_scroll: int):
        click_count = 0

        while True:
            if (
                number_endless_scroll is not None
                and click_count >= number_endless_scroll
            ):
                break

            try:
                self.driver.wait_and_click(
                    by="css selector",
                    wait_for=self.load_more_class,
                    timeout=10,
                )
                self.driver.scroll_to_bottom()
                click_count += 1
            except Exception:
                break

    def parse_entries(self, author: str) -> List[TopicBaseResponse]:
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        topics = soup.select(self.topic_class)
        results = []

        for item in topics:
            title_tag = item.select_one(self.title_class)
            content_div = item.select_one(self.content_class)
            date_tag = item.select_one(self.date_class)

            entry = TopicBaseResponse(
                title=title_tag.get_text(strip=True) if title_tag else None,
                content=content_div.get_text(separator=" ", strip=True)
                if content_div
                else None,
                date=date_tag.get_text(strip=True) if date_tag else None,
                author=author,
            )

            results.append(entry)

        return results


def get_author_entries(
    author: str,
    number_endless_scroll: int = 10,
    driver: Optional[DriverClient] = None,
    headless: bool = False,
    driver_path: Optional[str] = None,
    driver_version: Optional[int] = None,
    verbose: bool = False,
) -> List[Dict[str, str]]:
    """
    Get all entries made by a specific author.

    Args:
        author (str): The author's username.
        number_endless_scroll (int, optional): The number of times to perform endless scrolling. Defaults to 10.
        driver (Optional[DriverClient], optional): The driver client to use. Defaults to None.
        headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        driver_path (Optional[str], optional): The path to the browser driver. Defaults to None.
        driver_version (Optional[int], optional): The version of the browser driver. Defaults to None.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

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
    scraper = AuthorScraper(
        driver=driver,
        headless=headless,
        driver_path=driver_path,
        driver_version=driver_version,
        verbose=verbose,
    )
    entries = scraper.scrape(author=author, number_endless_scroll=number_endless_scroll)
    return entries
