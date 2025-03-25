import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..base_driver import BaseBrowser


class UCDriver(BaseBrowser):

    def __init__(self, headless=False, binary_location: str = None):
        options = uc.ChromeOptions()
        if binary_location:
            options.binary_location = binary_location
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')

        self.driver = uc.Chrome(options=options, version_main=136, headless=headless)

    def get_html(self, url: str, wait_for_class: str = None, timeout: int = 10) -> str:
        self.driver.get(url)
        if wait_for_class:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, wait_for_class))
                )
            except Exception as e:
                print(f"[WARN] Timeout waiting for class '{wait_for_class}': {e}")
        else:
            self.driver.implicitly_wait(timeout)
        return self.driver.page_source

    async def get_html_async(self, url: str, wait_for_class: str = None, timeout: int = 10) -> str:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            html = await loop.run_in_executor(
                pool, self.get_html, url, wait_for_class, timeout
            )
        return html
    
    def quit(self) -> None:
        self.driver.quit()
