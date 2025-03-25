import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import List, Dict
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver


def get_entry_from_url(
        url: str, 
        sync_driver: str = "uc", 
        headless: bool = False, 
        binary_location: str = None
        ) -> List[Dict[str, str]]:
    
    content_class = SELECTORS["entry_from_url"]["content"]
    author_class = SELECTORS["entry_from_url"]["author"]
    date_class = SELECTORS["entry_from_url"]["date"]
    title_class = SELECTORS["entry_from_url"]["title"]
    
    browser = get_browser_driver(sync_driver, headless=headless, binary_location=binary_location)
    driver = browser.driver

    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, content_class))
            )
        except Exception as e:
            print(f"[WARN] Entry content did not appear: {e}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        content_div = soup.select_one(content_class)
        author_a = soup.select_one(author_class)
        date_a = soup.select_one(date_class)
        title_h1 = soup.select_one(title_class)

        return {
            "content": content_div.get_text(separator=" ", strip=True) if content_div else None,
            "author": author_a.text.strip() if author_a else None,
            "date": date_a.text.strip() if date_a else None,
            "title": title_h1.text.strip() if title_h1 else None,
        }

    finally:
        browser.quit()