import requests
from bs4 import BeautifulSoup
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1490728017058594897/DxP9Gqo_9QRU0qtXF8T1j_d2zqHpzE9HWLmMyAq2JTTdqKlaTezLTk25oHqVCIvc8Pwd"
URL = "https://www.chromehearts.com/"
HISTORY_FILE = "link_history.txt"

def get_current_links():
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        # This grabs every clickable link text on the page (tabs, buttons, nav)
        links = {a.text.strip() for a in soup.find_all('a') if a.text.strip()}
        return links
    except Exception as e:
        print(f"Error fetching site: {e}")
        return set()

def monitor():
    current_links = get_current_links()
    
    # 1. Load the history from the last run
    if not os.path.exists(HISTORY_FILE):
        # First time running: save current links and exit
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_links)))
        print("Initial history created.")
        return

    with open(HISTORY_FILE, "r") as f:
        old_links = set(line.strip() for line in f.readlines())

    # 2. Find the "New" stuff (Difference between sets)
    new_items = current_links - old_links

    if new_items:
        added_text = ", ".join(new_items)
        msg = f"🚨 **CHROME HEARTS SITE UPDATE**\nNew Tab(s) Detected: **{added_text}**\nCheck here: {URL}"
        requests.post(WEBHOOK_URL, json={"content": msg})
        
        # 3. Update the history file with the new state
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_links)))
        print(f"Update found: {added_text}")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    monitor()
