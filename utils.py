import requests
from bs4 import BeautifulSoup
import re
import json
import time

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def extract_content(self, url):
        try:
            response = self.session.get(url, timeout=100)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title found"
            body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
            
            return body_text
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
    
    def clear_session(self):
        self.session.close()


def preprocess_text(raw_text):
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    start_idx = 0
    for i, line in enumerate(lines):
        if line.endswith('?'):
            start_idx = i
            break
    lines = lines[start_idx:]
    posts = []
    current_post = []
    for line in lines:
        if re.match(r'\d+[hd] ago', line) and current_post:
            posts.append(current_post)
            current_post = []
        current_post.append(line)
    if current_post:
        posts.append(current_post)
        
    return posts

def parse_filtered_text(post_lines):
    author = None
    if "by" in post_lines:
        try:
            idx = post_lines.index("by")
            author = post_lines[idx+1] if idx+1 < len(post_lines) else None
        except ValueError:
            pass
            
    timestamp = None
    for line in post_lines:
        m = re.search(r'\d+[hd] ago', line)
        if m:
            timestamp = m.group(0)
            break
            
    ignore_words = {"Upvote", "Report", "Share", "Add a comment", "Login to comment", "Replies", "Best"}
    content_lines = []
    for line in post_lines:
        if line in ignore_words:
            continue
        if re.match(r'\(\d+\)', line):
            continue
        content_lines.append(line)
    
    content = "\n".join(content_lines)
    return {"timestamp": timestamp, "content": content}
