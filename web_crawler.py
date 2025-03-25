import time
import json
import socket
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


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

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        html = fetch_dynamic_page(url, driver)
        if not html:
            continue

        send_to_transformer(url, html)

        # Extract and classify links
        links = extract_links(html, url)
        for link in links:
            if is_same_domain(link, whitelist_domain):
                if link not in visited:
                    to_visit.append(link)
            else:
                print(f"[External] {link}")

    driver.quit()


if __name__ == "__main__":
    crawl("https://projecteuler.net/about", "projecteuler.net")
