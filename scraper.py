from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from typing import List, Dict


class EksiScraper:

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.data = {}
        self._configure_driver()

    def _configure_driver(self) -> None:
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        return

    def scrap(self, urls: List[str]) -> Dict[str, List[str]]:
        for idx, url in enumerate(urls):

            if self.verbose:
                print(f"Scraping {url}")

            self.data[idx] = self._tour(url)

        return self.data
    
    def get_collected_data(self) -> Dict[str, List[str]]:
        return self.data
    
    def _tour(self, url: str):
        counter = 1
        text_list = []

        while True:
            current_url = url if counter == 1 else url + "?p=" + str(counter)
            self.driver.get(current_url)
            try:
                page_list = self._parse(self.driver.page_source)
                text_list.extend(page_list)
                if self.verbose and counter % 100 == 0:
                    print(f"{counter} pages are scraped, {len(text_list)} entries are collected")
            except Exception as e:
                print(e)
                if self.verbose:
                    print(f"Scraping finished for {url}, {counter} pages are scraped, {len(text_list)} entries are collected")
                break
            counter += 1
        return text_list
    
    def _parse(self, page_content: str) -> List[str]:
        page_list = []
        soup = BeautifulSoup(page_content, 'html.parser')
        divs = soup.find_all("div", {"class": "content"})
    
        if len(divs) == 0:
            raise Exception("No content found")
        
        for div in divs:
            page_list.append(div.get_text(strip=True))

        return page_list