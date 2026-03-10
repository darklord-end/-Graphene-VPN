import os
import re
import requests
import json
import base64
import subprocess
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
BRAND = "Graphene VPN"
DIR = "githubmirror"
FINAL_FILE = f"{DIR}/26.txt"
URLS = ["https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"]

def log(msg):
    print(f"[{BRAND}] {msg}")

class GrapheneSecurity:
    @staticmethod
    def is_safe(host):
        """Простейшая проверка: не является ли IP российским (если нужно отсечь RU-узлы)"""
        try:
            # Используем быстрый API для проверки геолокации
            # Если нужно именно ПРОВЕРЯТЬ из России (доступность), логика будет другой
            resp = requests.get(f"http://ip-api.com/json/{host}?fields=countryCode,status", timeout=2)
            data = resp.json()
            if data.get("status") == "success" and data.get("countryCode") == "RU":
                return False # Узел в РФ — потенциально под контролем/блокировкой
            return True
        except:
            return True # Если API упал, пропускаем (лучше оставить, чем удалить рабочее)

    @staticmethod
    def extract_host(link):
        try:
            if link.startswith("vmess://"):
                payload = link[8:]
                payload += "=" * ((4 - len(payload) % 4) % 4)
                data = json.loads(base64.b64decode(payload).decode('utf-8', errors='ignore'))
                return data.get('add')
            match = re.search(r'@([\w\.-]+):', link)
            return match.group(1) if match else None
        except:
            return None

def process_and_filter(links):
    safe_links = []
    log(f"Проверка безопасности для {len(links)} узлов...")
    
    # Проверяем в 10 потоков, чтобы Workflow не шел вечно
    with ThreadPoolExecutor(max_workers=10) as executor:
        hosts = [GrapheneSecurity.extract_host(l) for l in links]
        results = list(executor.map(GrapheneSecurity.is_safe, [h for h in hosts if h]))
        
        # Сопоставляем результаты (упрощенно)
        for i, link in enumerate([l for l in links if GrapheneSecurity.extract_host(l)]):
            if i < len(results) and results[i]:
                safe_links.append(link)
    
    return safe_links

def main():
    os.makedirs(DIR, exist_ok=True)
    all_configs = set()

    # 1. Сбор данных
    for url in URLS:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                found = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', r.text)
                all_configs.update(found)
        except Exception as e:
            log(f"Ошибка загрузки: {e}")

    # 2. Фильтрация (Безопасность)
    filtered = process_and_filter(list(all_configs))
    
    # 3. Сохранение
    with open(FINAL_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered))
    
    log(f"Итог: {len(filtered)} безопасных узлов сохранено.")

    # 4. GitHub Push (для Workflow)
    try:
        subprocess.run(["git", "config", "user.name", "GrapheneBot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@graphene.vpn"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"🚀 {BRAND}: Safe Update ({len(filtered)} nodes)"], check=True)
        subprocess.run(["git", "push"], check=True)
    except:
        log("Git Push пропущен (локальный запуск или нет изменений)")

if __name__ == "__main__":
    main()
