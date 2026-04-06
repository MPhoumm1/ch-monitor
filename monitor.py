import requests
from bs4 import BeautifulSoup
import os

# Grabs your secret from GitHub Settings
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
URL = "https://www.chromehearts.com/"
HISTORY_FILE = "link_history.txt"

def get_current_links():
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        # This grabs every link text (tabs, buttons, nav items)
        links = {a.text.strip() for a in soup.find_all('a') if a.text.strip()}
        return links
    except Exception as e:
        print(f"Error fetching site: {e}")
        return set()

def monitor():
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK secret is missing!")
        return

    current_links = get_current_links()
    if not current_links:
        print("Could not find any links on the page. Skipping this run.")
        return
    
    # 1. Load History
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_links)))
        print("Initial history created.")
        return

    with open(HISTORY_FILE, "r") as f:
        old_links = set(line.strip() for line in f.readlines())

    # 2. Compare
    new_items = current_links - old_links

    if new_items:
        added_text = ", ".join(new_items)
        msg = {"content": f"🚨 **CHROME HEARTS UPDATE**\nNew Tab(s): **{added_text}**\nLink: {URL}"}
        requests.post(WEBHOOK_URL, json=msg)
        
        # 3. Update History
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_links)))
        print(f"Update found: {added_text}")
    else:
        print("No changes detected. Site is the same.")

if __name__ == "__main__":
    monitor()
