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
        
        # New Logic: Grabs the text AND the link
        found_links = {}
        for a in soup.find_all('a', href=True):
            text = a.text.strip()
            link = a['href']
            if text:
                # If it's a relative link (like /shop), make it full (https://chromehearts.com/shop)
                if link.startswith('/'):
                    link = f"https://www.chromehearts.com{link}"
                found_links[text] = link
        return found_links
    except Exception as e:
        print(f"Error fetching site: {e}")
        return {}

def monitor():
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK secret is missing!")
        return

    current_data = get_current_links()
    if not current_data:
        print("Could not find any links. Skipping.")
        return
    
    # 1. Load History (just the keys/names of the links)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_data.keys())))
        print("Initial history created.")
        return

    with open(HISTORY_FILE, "r") as f:
        old_link_names = set(line.strip() for line in f.readlines())

    # 2. Compare what's NEW
    new_items = set(current_data.keys()) - old_link_names

    if new_items:
        # Create a nice list of clickable links for Discord
        alert_lines = []
        for item in new_items:
            link = current_data[item]
            alert_lines.append(f"🔗 **[{item}]({link})**")
        
        message_body = "\n".join(alert_lines)
        
        # 3. Send to Discord
        payload = {
            "content": f"🚨 **CHROME HEARTS DROP DETECTED**\n\n{message_body}\n\nClick the link above to shop now!"
        }
        requests.post(WEBHOOK_URL, json=payload)
        
        # 4. Update History
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(sorted(current_data.keys())))
        print(f"Update found and sent: {', '.join(new_items)}")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    monitor()
