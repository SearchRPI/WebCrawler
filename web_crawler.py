import requests
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin

def create_driver():
    """Initialize a Selenium WebDriver for dynamic page fetching."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return webdriver.Chrome(service=Service("/opt/homebrew/bin/chromedriver"), options=options)

def fetch_static_page(url):
    """Fetch a static page using requests."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return url, soup.prettify()
    except requests.RequestException as e:
        print(f"Static fetch failed for {url}: {e}")
        return url, None

def fetch_dynamic_page(url, driver):
    """Fetch a dynamic page using Selenium."""
    try:
        driver.get(url)
        # Use WebDriverWait to ensure the page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return url, soup.prettify()
    except Exception as e:
        print(f"Dynamic fetch failed for {url}: {e}")
        return url, None

def crawl(start_url, max_pages=50):
    """Crawl web pages, handling both static and dynamic rendering."""
    to_visit = [start_url]
    visited = set()
    data = {}

    print(f"Starting crawl with start_url={start_url}, max_pages={max_pages}")

    driver = create_driver()

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        url, html = fetch_static_page(url)
        if not html:
            url, html = fetch_dynamic_page(url, driver)

        if html:
            data[url] = html

            # Add links `to_visit`
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a', href=True):
                new_url = urljoin(url, link['href'])
                if new_url not in visited and new_url not in to_visit:
                    to_visit.append(new_url)

    driver.quit()
    return data

if __name__ == "__main__":
    start_url = "https://projecteuler.net/about"
    crawled_data = crawl(start_url)

    for i, (url, html) in enumerate(crawled_data.items(), start=1):
        print(f"{i}: Fetched {url} with {len(html)} characters of HTML")
