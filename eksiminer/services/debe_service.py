import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver


def get_debe_list(sync_driver: str = "uc", headless: bool = False, binary_location: str = None) -> List[Dict[str, str]]:
    wait_for_class = SELECTORS["debe"]["wait_for_class"]
    container_class = SELECTORS["debe"]["container"]
    debe_website = SELECTORS["debe_website"]

    browser = get_browser_driver(sync_driver, headless=headless, binary_location=binary_location)
    driver = browser.driver

    try:
        driver.get(debe_website)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, wait_for_class))
            )
        except Exception as e:
            print(f"[WARN] Topic list did not appear: {e}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        a_tags = soup.select(container_class)

        results = []
        for a_tag in a_tags:
            href = a_tag.get("href")
            title = a_tag.get_text(strip=True)
            full_url = f"https://eksisozluk.com{href}"
            results.append({"title": title, "url": full_url})

        return results

    finally:
        browser.quit()
