import os
import re
import json
import base64
import requests
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- CONFIG ---
BRAND = "⬢ Graphene"
DIR = "githubmirror"
FREE_FILE = f"{DIR}/26.txt"
PREM_FILE = f"{DIR}/premium.txt"

SOURCES = ["https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"]

# Расширенная база: добавил Азию, Европу и СНГ
GEO_DATA = {
    "DE": ("🇩🇪", "Germany"), "US": ("🇺🇸", "USA"), "FI": ("🇫🇮", "Finland"),
    "PL": ("🇵🇱", "Poland"), "NL": ("🇳🇱", "Netherlands"), "FR": ("🇫🇷", "France"),
    "GB": ("🇬🇧", "UK"), "TR": ("🇹🇷", "Turkey"), "KZ": ("🇰🇿", "Kazakhstan"),
    "SG": ("🇸🇬", "Singapore"), "JP": ("🇯🇵", "Japan"), "HK": ("🇭🇰", "Hong Kong"),
    "EE": ("🇪🇪", "Estonia"), "KR": ("🇰🇷", "Korea"), "CA": ("🇨🇦", "Canada"),
    "AT": ("🇦🇹", "Austria"), "CH": ("🇨🇭", "Switzerland"), "UA": ("🇺🇦", "Ukraine"),
    "ES": ("🇪🇸", "Spain"), "IT": ("🇮🇹", "Italy"), "UN": ("🌐", "Global")
}

class GrapheneEngine:
    def __init__(self):
        os.makedirs(DIR, exist_ok=True)

    def get_geo_info(self, host, original_link):
        """Улучшенный поиск гео: API + поиск в тексте ссылки"""
        # 1. Сначала пробуем вытащить код из названия (самый быстрый способ)
        for code in GEO_DATA.keys():
            if code != "UN" and (f"_{code}" in original_link.upper() or f"-{code}" in original_link.upper()):
                return GEO_DATA[code]

        # 2. Если в названии нет, идем в API
        try:
            r = requests.get(f"http://ip-api.com/json/{host}?fields=countryCode", timeout=1.0).json()
            code = r.get("countryCode", "UN")
            return GEO_DATA.get(code, GEO_DATA["UN"])
        except:
            return GEO_DATA["UN"]

    def format_link(self, link, index, is_premium=False):
        try:
            base = link.split('#')[0]
            host = ""
            if "vmess://" in link:
                # Фикс паддинга для vmess
                payload = link[8:]
                payload += "=" * ((4 - len(payload) % 4) % 4)
                data = json.loads(base64.b64decode(payload).decode('utf-8', ignore='ignore'))
                host = data.get('add')
            else:
                m = re.search(r'@([\w\.-]+):', link)
                if m: host = m.group(1)

            flag, country = self.get_geo_info(host, link)
            status = "Premium" if is_premium else "Free"
            
            # Чистый стиль по твоему запросу
            new_name = f"{flag} {country} | {status}"
            return f"{base}#{urllib.parse.quote(new_name)}"
        except:
            return link

    def run(self):
        print(f"[{BRAND}] Starting build...")
        try:
            resp = requests.get(SOURCES[0], timeout=15)
            # Улучшенная регулярка, чтобы не пропускать странные порты
            raw_links = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', resp.text)
        except:
            raw_links = []

        # Free (25 серверов), Premium (остальные)
        free_nodes = raw_links[:25]
        prem_nodes = raw_links[25:125] 

        # Сборка файлов (с твоей крутой подписью плана)
        self.write_sub(FREE_FILE, free_nodes, "GRAPHENE VPN | ПЛАН: FREE", "LIFETIME")
        self.write_sub(PREM_FILE, prem_nodes, "ПЛАН: ULTRA PREMIUM 💎", "ACTIVE")

        self.deploy()

    def write_sub(self, path, nodes, plan_name, status):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote(f'⬢ {plan_name}')}\n")
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote(f'⬢ СТУТС: {status}')}\n")
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote('⬢ ПОДДЕРЖКА: @Graphene_Bot')}\n")
            for i, l in enumerate(nodes):
                f.write(self.format_link(l, i+1, "PREMIUM" in plan_name) + "\n")

    def deploy(self):
        subprocess.run(["git", "config", "user.name", "GrapheneBot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@graphene.vpn"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout:
            subprocess.run(["git", "commit", "-m", "🚀 Graphene Geo-Update"], check=True)
            subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    GrapheneEngine().run()
