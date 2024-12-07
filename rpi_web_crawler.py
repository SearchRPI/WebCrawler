from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from urllib.parse import urljoin

def crawl(start_url, max_pages=50):
    """
    A simple web crawler for static pages.
    
    Args:
        start_url (str): The starting URL for the crawl.
        max_pages (int): The maximum number of pages to crawl.

    Returns:
        dict: A dictionary where keys are URLs and values are their HTML content.
    """
    # Configure Selenium
    service = Service("/opt/homebrew/bin/chromedriver")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    # The path to the chrome browser
    driver = webdriver.Chrome(service=service, options=options)

    to_visit = [start_url]  # List of URLs to visit
    visited = set()         # Set of visited URLs
    data = {}               # Dictionary to store URL and HTML content

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            # Load the page
            driver.get(url)
            # TODO: Adjust the time to sleep for JS calls
            time.sleep(1)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        visited.add(url)
        data[url] = soup.prettify()

        # Find all links on the page
        for link in soup.find_all('a', href=True):
            new_url = urljoin(url, link['href'])
            if new_url not in visited and new_url not in to_visit:
                to_visit.append(new_url)

    driver.quit()
    return data

if __name__ == "__main__":
    # Testing the crawler with the Project Euler website
    start_url = "https://projecteuler.net/about"
    crawled_data = crawl(start_url)

    # Display the results
    i = 1;
    for url, html in crawled_data.items():
        print(f"{i}: Fetched {url} with {len(html)} characters of HTML")
        i += 1
