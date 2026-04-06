import requests
from bs4 import BeautifulSoup
import os
import time
import random

# Grabs your secret from GitHub Settings
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
URL = "https://www.chromehearts.com/"
HISTORY_FILE = "link_history.txt"

# --- ADD WORDS TO IGNORE HERE ---
BLACKLIST = ["Bag", "Cart", "Account", "Log In", "Checkout", "View Cart"]

def get_current_links():
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_links = {}
        for a in soup.find_all('a', href=True):
            text = a.text.strip()
            link = a['href']
            
            # FILTER: Skip if text is empty OR if it's in our Blacklist
            if not text or any(word.lower() in text.lower() for word in BLACKLIST):
                continue

            if link.startswith('/'):
                link = f"https://www.chromehearts.com{link}"
            found_links[text] = link
        return found_links
    except Exception as e:
        print(f"Error fetching site: {e}")
        return {}

def monitor():
    # --- STEALTH DELAY ---
    # Wait between 1 and 30 seconds before starting
    time.sleep(random.randint(1, 30)) 
    
    if not WEBHOOK_URL:
        return

    current_data = get_current_links()
    if not current_data:
        return
    
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_data.keys())))
        return

    with open(HISTORY_FILE, "r") as f:
        old_link_names = set(line.strip() for line in f.readlines())

    new_items = set(current_data.keys()) - old_link_names

    if new_items:
        alert_lines = [f"🔗 **[{item}]({current_data[item]})**" for item in new_items]
        message_body = "\n".join(alert_lines)
        
        payload = {
            "content": f"🚨 **CHROME HEARTS DROP DETECTED**\n\n{message_body}"
        }
        requests.post(WEBHOOK_URL, json=payload)
        
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_data.keys())))

if __name__ == "__main__":
    monitor()
