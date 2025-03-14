import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin, urlparse

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
    """Fetch a dynamic page using Selenium and return the full HTML."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return driver.page_source  # Return full raw HTML
    except Exception as e:
        print(f"Dynamic fetch failed for {url}: {e}")
        return None

def crawl(start_url, whitelist_domain, max_pages=50):
    """Crawl web pages dynamically, fetching full HTML and BFS-traversing links."""
    to_visit = [start_url]
    visited = set()
    crawled_data = []

    print(f"Starting crawl: start_url={start_url}, max_pages={max_pages}, whitelist_domain={whitelist_domain}")

    driver = create_driver()

    with open("external_urls.txt", "w") as external_file:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            html = fetch_dynamic_page(url, driver)
            if not html:
                continue

            # Extract links for BFS traversal
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            for link in soup.find_all('a', href=True):
                new_url = urljoin(url, link['href'])
                parsed_url = urlparse(new_url)
                if parsed_url.netloc == whitelist_domain:
                    if new_url not in visited and new_url not in to_visit:
                        to_visit.append(new_url)
                        links.append(new_url)
                else:
                    external_file.write(f"{new_url}\n")

            # Store full HTML for text transformer
            crawled_data.append({
                "url": url,
                "html": html,
                "links": links
            })

    driver.quit()
    return crawled_data

if __name__ == "__main__":
    start_url = "https://projecteuler.net/about"
    whitelist_domain = "projecteuler.net"
    crawled_data = crawl(start_url, whitelist_domain)

    # Save full HTML data for the text transformer
    with open("crawled_data.json", "w") as f:
        json.dump(crawled_data, f, indent=4)

    # Print summary
    for i, page in enumerate(crawled_data, start=1):
        print(f"{i}: Processed {page['url']} ({len(page['html'])} characters of HTML)")
