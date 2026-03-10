import os
import re
import json
import base64
import requests
import subprocess
import urllib.parse

# --- CONFIG ---
BRAND = "⬢ Graphene"
DIR = "githubmirror"
FREE_FILE = f"{DIR}/26.txt"
PREM_FILE = f"{DIR}/premium.txt"

# Твой основной источник
SOURCES = ["https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"]

# Флаги и названия
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

    def get_geo_info(self, host):
        try:
            # Быстрая проверка гео
            r = requests.get(f"http://ip-api.com/json/{host}?fields=countryCode", timeout=1.2).json()
            code = r.get("countryCode", "UN")
            return GEO_DATA.get(code, GEO_DATA["UN"])
        except:
            return GEO_DATA["UN"]

    def format_link(self, link, index, is_premium=False):
        try:
            base = link.split('#')[0]
            host = ""
            # Извлекаем хост для определения страны
            if "vmess://" in link:
                data = json.loads(base64.b64decode(link[8:] + "==").decode('utf-8', ignore='ignore'))
                host = data.get('add')
            else:
                m = re.search(r'@([\w\.-]+):', link)
                if m: host = m.group(1)

            flag, country = self.get_geo_info(host)
            status = "Premium" if is_premium else "Free"
            
            # Тот самый чистый стиль: Флаг Страна | Тариф
            # Пример: 🇩🇪 Germany | Free
            new_name = f"{flag} {country} | {status}"
            
            return f"{base}#{urllib.parse.quote(new_name)}"
        except:
            return link

    def run(self):
        print(f"[{BRAND}] Starting build...")
        
        # Загрузка сырых данных
        try:
            resp = requests.get(SOURCES[0], timeout=10)
            raw_links = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', resp.text)
        except:
            raw_links = []

        # Разделение на Free (25) и Premium (все остальные)
        free_nodes = raw_links[:25]
        prem_nodes = raw_links[25:100] # Заглушка для премиума

        # Сборка Free
        with open(FREE_FILE, "w", encoding="utf-8") as f:
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote('⬢ GRAPHENE VPN | ПЛАН: FREE')}\n")
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote('⬢ ПОДДЕРЖКА: @Graphene_Bot')}\n")
            for i, l in enumerate(free_nodes):
                f.write(self.format_link(l, i+1, False) + "\n")

        # Сборка Premium
        with open(PREM_FILE, "w", encoding="utf-8") as f:
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote('⬢ ПЛАН: ULTRA PREMIUM 💎')}\n")
            f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote('⬢ ДОСТУП: LIFETIME')}\n")
            for i, l in enumerate(prem_nodes):
                f.write(self.format_link(l, i+1, True) + "\n")

        self.deploy()

    def deploy(self):
        subprocess.run(["git", "config", "user.name", "GrapheneBot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@graphene.vpn"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout:
            subprocess.run(["git", "commit", "-m", "🚀 Graphene Sync"], check=True)
            subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    GrapheneEngine().run()
