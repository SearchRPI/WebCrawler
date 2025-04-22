import time
import json
import socket
import os
import argparse
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawler_logger import init_log, log_page_visit

TRANSFORMER_HOST = 'localhost'
TRANSFORMER_PORT = 9001

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return webdriver.Chrome(service=Service("/opt/homebrew/bin/chromedriver"), options=options)

def fetch_dynamic_page(url, driver):
    try:
        start_time = time.time()
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        elapsed = time.time() - start_time
        return driver.page_source, elapsed
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None, None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag['href']
        full_url = urljoin(base_url, href)
        links.add(full_url)
    return links

def is_same_domain(url, whitelist_domain):
    try:
        return urlparse(url).netloc.endswith(whitelist_domain)
    except:
        return False

def send_to_transformer(url, html):
    try:
        with socket.create_connection((TRANSFORMER_HOST, TRANSFORMER_PORT)) as sock:
            message = json.dumps({"url": url, "html": html})
            sock.sendall((message + "\n").encode())
    except Exception as e:
        print(f"Error sending to transformer: {e}")

def crawl(start_url, whitelist_domain, max_pages=50):
    to_visit = [start_url]
    visited = set()
    print(f"Crawling starting at {start_url}")

    driver = create_driver()
    init_log()

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        html, load_time = fetch_dynamic_page(url, driver)
        if not html:
            log_page_visit(url, status="failed")
            continue

        send_to_transformer(url, html)

        content_size = len(html.encode('utf-8'))
        links = extract_links(html, url)
        internal_links = [link for link in links if is_same_domain(link, whitelist_domain)]
        external_links = [link for link in links if not is_same_domain(link, whitelist_domain)]

        log_page_visit(
            url,
            load_time=load_time,
            content_size=content_size,
            total_links=len(links),
            internal_links=len(internal_links),
            external_links=len(external_links),
            status="success"
        )

        for link in internal_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Run the SearchRPI web crawler.")
    parser.add_argument("--start", type=str, required=True, help="Starting URL to crawl")
    parser.add_argument("--domain", type=str, required=True, help="Domain whitelist (e.g., rpi.edu)")
    parser.add_argument("--max", type=int, default=50, help="Maximum number of pages to crawl")
    args = parser.parse_args()

    crawl(args.start, args.domain, args.max)

if __name__ == "__main__":
    main()
