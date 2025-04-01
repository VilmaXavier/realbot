import requests
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_URL = "https://xaviers.ac/"
OUTPUT_FILE = "all_urls.json"

# Set to store unique URLs
visited_urls = set()

def get_internal_links(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            full_url = urljoin(BASE_URL, href)
            parsed_url = urlparse(full_url)
            
            # Ensure the link belongs to the same domain and is not a file (PDF, DOC, etc.)
            if parsed_url.netloc == urlparse(BASE_URL).netloc and not full_url.endswith((".pdf", ".doc", ".docx")):
                links.add(full_url)
        
        return links
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return set()

def crawl_website():
    to_visit = {BASE_URL}
    
    while to_visit:
        current_url = to_visit.pop()
        if current_url not in visited_urls:
            print(f"Scraping: {current_url}")
            visited_urls.add(current_url)
            new_links = get_internal_links(current_url)
            to_visit.update(new_links - visited_urls)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(visited_urls), f, indent=4)
    
    print(f"Saved {len(visited_urls)} URLs to {OUTPUT_FILE}")

if __name__ == "__main__":
    crawl_website()