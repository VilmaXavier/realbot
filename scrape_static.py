import os
import json
import time
import requests
from bs4 import BeautifulSoup

STATIC_DATA_FILE = "college_static.json"
URLS_FILE = "all_urls.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def load_urls():
    """Load URLs from file and ensure no duplicates."""
    if not os.path.exists(URLS_FILE):
        print(f"Error: {URLS_FILE} not found.")
        return []
    
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)
    
    # Remove duplicate URLs by converting list to a set and back to a list
    return list(set(urls))

def scrape_page(url):
    """Scrape the page content from the provided URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        if "text/html" not in response.headers.get("Content-Type", ""):
            print(f"Skipping non-HTML content: {url}")
            return None
    except requests.HTTPError as e:
        print(f"Failed to fetch {url}: {e}")
        return None
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = " ".join([p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    return {"url": url, "content": text_content}

def scrape_static():
    """Main function to scrape static content from the URLs."""
    urls = load_urls()
    if not urls:
        print("No URLs to scrape.")
        return
    
    static_data = {}
    
    for url in urls:
        print(f"Scraping: {url}")
        page_data = scrape_page(url)
        if page_data:
            static_data[url] = page_data
        time.sleep(1)  # Avoid overwhelming the server
    
    # Save the scraped data to a JSON file
    with open(STATIC_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(static_data, f, indent=4)

    print(f"Static data saved to {STATIC_DATA_FILE}")

if __name__ == "__main__":
    scrape_static()
