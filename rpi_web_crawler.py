import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def crawl(start_url, max_pages=1500):
    """
    A simple web crawler for static pages.
    
    Args:
        start_url (str): The starting URL for the crawl.
        max_pages (int): The maximum number of pages to crawl.

    Returns:
        dict: A dictionary where keys are URLs and values are their HTML content.
    """
    to_visit = [start_url]  # List of URLs to visit
    visited = set()         # Set of visited URLs
    data = {}               # Dictionary to store URL and HTML content

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            # Fetch the HTML content
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        visited.add(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        data[url] = soup.prettify()  # Store the prettified HTML

        # Find all links on the page
        for link in soup.find_all('a', href=True):
            new_url = urljoin(url, link['href'])
            if new_url not in visited and new_url not in to_visit:
                to_visit.append(new_url)

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
