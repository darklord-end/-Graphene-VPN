import os
import re
import json
import base64
import requests
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- КОНФИГУРАЦИЯ ---
BRAND_NAME = "⬢ Graphene VPN"
DIR = "githubmirror"
FREE_FILE = f"{DIR}/26.txt"
PREMIUM_FILE = f"{DIR}/premium.txt"

# Источники
FREE_SOURCES = ["https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"]
# Пока заглушка для премиума (можешь добавить свои секретные URL)
PREMIUM_SOURCES = [
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt" 
]

LOCATIONS = {
    "DE": "Germany", "US": "USA", "FI": "Finland", "PL": "Poland", 
    "NL": "Netherlands", "FR": "France", "GB": "United Kingdom", "TR": "Turkey"
}

class GrapheneEngine:
    def __init__(self):
        os.makedirs(DIR, exist_ok=True)

    def get_geo(self, host):
        try:
            r = requests.get(f"http://ip-api.com/json/{host}?fields=countryCode", timeout=1.5).json()
            return r.get("countryCode", "UN")
        except:
            return "UN"

    def rebrand_link(self, link, index, is_premium=False):
        try:
            base_part = link.split('#')[0]
            host = ""
            if "vmess://" in link:
                v_data = json.loads(base64.b64decode(link[8:] + "==").decode('utf-8', ignore='ignore'))
                host = v_data.get('add')
            else:
                match = re.search(r'@([\w\.-]+):', link)
                if match: host = match.group(1)

            country_code = self.get_geo(host)
            country_name = LOCATIONS.get(country_code, "Elite Route")
            
            tag = "PREMIUM" if is_premium else "FREE"
            icon = "💎" if is_premium else "⚡"
            
            new_name = f"{BRAND_NAME} | {icon} {country_name} #{index} [{tag}]"
            return f"{base_part}#{urllib.parse.quote(new_name)}"
        except:
            return link

    def fetch_links(self, sources):
        links = set()
        for url in sources:
            try:
                res = requests.get(url, timeout=10)
                found = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', res.text)
                links.update(found)
            except: pass
        return list(links)

    def save_subscription(self, filename, links, status_text):
        with open(filename, "w", encoding="utf-8") as f:
            # Инфо-панель в приложении
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote(BRAND_NAME + ' | ' + status_text)}\n")
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#⬢_Support:_@your_tele_bot\n")
            f.write("\n".join(links))

    def run(self):
        # 1. Обработка FREE (20-25 штук)
        print("Сборка FREE подписки...")
        free_raw = self.fetch_links(FREE_SOURCES)[:25]
        free_final = [self.rebrand_link(l, i+1, False) for i, l in enumerate(free_raw)]
        self.save_subscription(FREE_FILE, free_final, "План: Free (Limited)")

        # 2. Обработка PREMIUM (Много)
        print("Сборка PREMIUM подписки...")
        prem_raw = self.fetch_links(PREMIUM_SOURCES)[:100] # Заглушка берет больше
        prem_final = [self.rebrand_link(l, i+1, True) for i, l in enumerate(prem_raw)]
        self.save_subscription(PREMIUM_FILE, prem_final, "План: Lifetime Ultra 💎")

        self.deploy()

    def deploy(self):
        try:
            subprocess.run(["git", "config", "user.name", "GrapheneBot"], check=True)
            subprocess.run(["git", "config", "user.email", "bot@graphene.vpn"], check=True)
            subprocess.run(["git", "add", "."], check=True)
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
            if status:
                subprocess.run(["git", "commit", "-m", f"🚀 {BRAND_NAME}: Update Free & Premium nodes"], check=True)
                subprocess.run(["git", "push"], check=True)
                print("Синхронизация завершена!")
        except Exception as e:
            print(f"Ошибка Git: {e}")

if __name__ == "__main__":
    GrapheneEngine().run()
