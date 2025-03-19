import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json

class WebScrapper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
    
        self.driver = webdriver.Chrome(options=chrome_options)

    def extract_content(self,url):
        # print(f"Navigating to {url}")
        self.driver.get(url)
        
        # Wait for the page to load completely
        # print("Waiting for page to load...")
        wait = WebDriverWait(self.driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Additional wait for dynamic content to load
        # time.sleep(5)
        
        # Extract the title
        title = self.driver.title
        # print("\n" + "="*50)
        # print(f"TITLE: {title}")
        # print("="*50)

        # print("No comments could be extracted from the page.")
        # # Try a last resort approach - get all text from the page
        # print("\nLAST RESORT - EXTRACTING ALL TEXT FROM PAGE:")
        # print("-"*50)
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        # print(body_text[:1000] + "..." if len(body_text) > 1000 else body_text)
    
        return body_text

    def clear_driver(self):
        self.driver.quit()


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
