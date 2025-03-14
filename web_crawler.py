import time
import json
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CRAWLER_PIPE = "/tmp/crawler_pipe"

def create_driver():
    """Initialize a Selenium WebDriver for dynamic page fetching."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return webdriver.Chrome(service=Service("/opt/homebrew/bin/chromedriver"), options=options)

def fetch_dynamic_page(url, driver):
    """Fetch a dynamic page using Selenium."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source  # Return full raw HTML
    except Exception as e:
        print(f"Dynamic fetch failed for {url}: {e}")
        return None

def crawl(start_url, whitelist_domain, max_pages=50):
    """Crawl web pages dynamically and send data to the Text Transformer via pipe."""
    to_visit = [start_url]
    visited = set()
    
    print(f"Starting crawl: {start_url} (max {max_pages} pages)")

    # Ensure the named pipe exists
    if not os.path.exists(CRAWLER_PIPE):
        os.mkfifo(CRAWLER_PIPE)

    driver = create_driver()

    with open(CRAWLER_PIPE, "w") as pipe:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            html = fetch_dynamic_page(url, driver)
            if not html:
                continue

            # Write URL + HTML to the pipe
            page_data = json.dumps({"url": url, "html": html})
            pipe.write(page_data + "\n")  # Send one JSON entry at a time

    driver.quit()

if __name__ == "__main__":
    start_url = "https://projecteuler.net/about"
    whitelist_domain = "projecteuler.net"
    crawl(start_url, whitelist_domain)
