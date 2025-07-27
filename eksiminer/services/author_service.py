import time
from bs4 import BeautifulSoup
from slugify import slugify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver


class AuthorScraper:

    def __init__(
            self,
            author: str,
            driver_name: str = "uc",
            headless: bool = False,
            click_threshold: int = 10,
            binary_location: Optional[str] = None,
            version_main: Optional[int] = None
    ):
        self.author = slugify(author)
        self.driver_name = driver_name
        self.headless = headless
        self.browser = get_browser_driver(
            name=driver_name, headless=headless, binary_location=binary_location, version_main=version_main
        )
        self.driver = self.browser.driver
        self.click_threshold = click_threshold
        self.entries = []

    def scrape(self) -> List[Dict[str, str]]:
        try:
            url = f"https://eksisozluk.com/biri/{self.author}"
            self.driver.get(url)
            self.scroll_to_bottom()
            self.load_all_entries()
            self.entries = self.parse_entries()
            return self.entries
        finally:
            self.browser.quit()

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def load_all_entries(self) -> None:
        load_more_class = SELECTORS["author"]["load_more"]
        click_count = 0

        while True:
            if self.click_threshold is not None and click_count >= self.click_threshold:
                print(
                    f"[INFO] Reached click threshold: {self.click_threshold}")
                break

            try:
                load_more = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, load_more_class))
                )
                load_more.click()
                time.sleep(2)
                self.scroll_to_bottom()
                click_count += 1
            except:
                break

    def parse_entries(self) -> List[Dict[str, str]]:
        topic_class = SELECTORS["author"]["topic"]
        title_class = SELECTORS["author"]["title"]
        content_class = SELECTORS["author"]["content"]
        date_class = SELECTORS["author"]["date"]

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        topics = soup.select(topic_class)
        results = []

        for item in topics:
            title_tag = item.select_one(title_class)
            content_div = item.select_one(content_class)
            date_tag = item.select_one(date_class)

            entry = {
                "title": title_tag.get_text(strip=True) if title_tag else None,
                "content": content_div.get_text(separator=" ", strip=True) if content_div else None,
                "date": date_tag.get_text(strip=True) if date_tag else None,
            }
            results.append(entry)

        return results
