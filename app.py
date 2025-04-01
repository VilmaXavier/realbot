import os
import json
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://xaviers.ac/"
STATIC_DATA_FILE = "college_static.json"
NOTICES_DATA_FILE = "college_notices.json"
GPT_MODEL = "llama3-8b-8192"
GROQ_API_KEY = "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"  # Replace with actual Groq API key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

NOTICE_URLS = [
    "https://xaviers.ac/student-support/notices/senior-college",
    "https://xaviers.ac/student-support/notices/junior-college"
]

# Function to scrape a single page
def scrape_page(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        if "text/html" not in response.headers.get("Content-Type", ""):
            print(f"Skipping non-HTML content: {url}")
            return None
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = " ".join([p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
    return {"url": url, "content": text_content}

# Function to scrape notices
def scrape_notices():
    notices_data = {}
    for url in NOTICE_URLS:
        print(f"Scraping: {url}")
        page_data = scrape_page(url)
        if page_data:
            notices_data[url] = page_data
    
    with open(NOTICES_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notices_data, f, indent=4)

# Load data from file
def load_data():
    static_data = {}
    if os.path.exists(STATIC_DATA_FILE):
        with open(STATIC_DATA_FILE, "r", encoding="utf-8") as f:
            static_data = json.load(f)
    
    notices_data = {}
    if os.path.exists(NOTICES_DATA_FILE):
        with open(NOTICES_DATA_FILE, "r", encoding="utf-8") as f:
            notices_data = json.load(f)
    
    return {**static_data, **notices_data}

@app.route("/")
def home():
    return "Chatbot API is running. Use POST /chat to interact."

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    data = load_data()
    context = " ".join([entry['content'] for entry in data.values()])
    
    payload = {
        "model": GPT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant providing brief and precise answers based on college information. Include relevant links where applicable."},
            {"role": "user", "content": f"Here is some college data: {context}. Now, answer this concisely: {user_input}"}
        ]
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        error_message = response.json().get("error", {}).get("message", "Unknown error")
        return jsonify({"error": f"Failed to get response from Groq API: {error_message}"}), 500
    
    answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
    
    return jsonify({"response": answer})

if __name__ == "__main__":
    scrape_notices()
    app.run(debug=True)