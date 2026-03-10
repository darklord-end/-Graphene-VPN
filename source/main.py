import os
import re
import json
import base64
import requests
import socket
import urllib.parse
import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# --- CONFIG ---
DIR = "githubmirror"
raw_key = os.getenv("PREMIUM_KEY", "default_local_key")
secure_hash = hashlib.sha256(raw_key.encode()).hexdigest()[:20]

FREE_FILE = f"{DIR}/26.txt"
PREM_FILE = f"{DIR}/{secure_hash}.txt" 
BRAND = "⬢ Graphene"
SOURCES = ["https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"]

class GrapheneEngine:
    def __init__(self):
        os.makedirs(DIR, exist_ok=True)
        self.update_time = datetime.now().strftime("%d.%m %H:%M")

    def check_node(self, host, port, timeout=1.5):
        """Проверка: живой ли порт"""
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                return True
        except: return False

    def parse_link(self, link):
        """Разбор ссылки и извлечение оригинального названия с эмодзи"""
        try:
            # Вытаскиваем название после решетки #
            parts = link.split('#')
            base_link = parts[0]
            original_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else "Global Server"

            # Извлекаем хост и порт для проверки связи
            if link.startswith("vmess://"):
                p = base_link[8:]; p += "=" * ((4 - len(p) % 4) % 4)
                data = json.loads(base64.b64decode(p).decode('utf-8', ignore='ignore'))
                return data.get('add'), data.get('port'), base_link, original_name
            
            match = re.search(r'@([\w\.-]+):(\d+)', base_link)
            if match: return match.group(1), match.group(2), base_link, original_name
        except: pass
        return None, None, None, None

    def process_node(self, link, index, is_premium):
        host, port, base, org_name = self.parse_link(link)
        
        # Проверяем только на "живучесть". Если порт открыт — берем!
        if not host or not self.check_node(host, port):
            return None
        
        status = "Premium" if is_premium else "Free"
        server_num = str(index).zfill(2)
        
        # Оставляем оригинальное название (с эмодзи и страной), добавляя наш бренд
        # Пример: ⬢ 🇩🇪 Germany | Server (01) [Free]
        new_name = f"{BRAND} {org_name} | Server ({server_num}) [{status}]"
        return f"{base}#{urllib.parse.quote(new_name)}"

    def write_sub(self, path, nodes, title):
        with open(path, "w", encoding="utf-8") as f:
            header = [
                f"⬢ {title} ⬢",
                f"Обновлено: {self.update_time}",
                f"Инфо: Используйте оригинальный софт",
                f"Статус: Прямое подключение ✅",
                f"Поддержка: @Graphene_Bot",
                "--------------------------------"
            ]
            for line in header:
                f.write(f"vless://0@0.0.0.0:0?encryption=none&security=none#{urllib.parse.quote(line)}\n")
            f.write("\n".join(nodes))

    def run(self):
        print(f"[{BRAND}] Чтение готовых данных из источника...")
        try:
            raw = requests.get(SOURCES[0], timeout=15).text
            links = list(dict.fromkeys(re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', raw)))
        except: return

        with ThreadPoolExecutor(max_workers=25) as executor:
            # Работаем с первыми 250 ссылками (там самый сок с эмодзи)
            results = list(executor.map(lambda x: self.process_node(x[1], x[0]+1, x[0] >= 25), enumerate(links[:250])))
            
            all_valid = [r for r in results if r]
            free_nodes = all_valid[:25]
            prem_nodes = all_valid[25:125]

        self.write_sub(FREE_FILE, free_nodes, "GRAPHENE | Бесплатно")
        self.write_sub(PREM_FILE, prem_nodes, "GRAPHENE ULTRA PREMIUM 💎")
        print(f"[{BRAND}] Готово! Собрано из оригинала.")

if __name__ == "__main__":
    GrapheneEngine().run()
