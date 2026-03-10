import os
import re
import requests
import subprocess

# --- КОНФИГУРАЦИЯ ---
BRAND = "Graphene VPN"
GITHUB_MIRROR_DIR = "githubmirror"
FINAL_FILE = f"{GITHUB_MIRROR_DIR}/26.txt"

# Твой список источников
URLS = [
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt"
]

def log(message):
    print(f"[{BRAND}] {message}")

def get_configs():
    unique_configs = set()
    
    # 1. Загрузка из основного URL
    for url in URLS:
        try:
            log(f"Загрузка: {url}")
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                # Вытаскиваем все ссылки по протоколам
                found = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', resp.text)
                unique_configs.update(found)
        except Exception as e:
            log(f"Ошибка при загрузке {url}: {e}")

    # 2. Чтение локальных файлов 1-25 (если они уже скачаны твоим старым кодом)
    for i in range(1, 26):
        path = f"{GITHUB_MIRROR_DIR}/{i}.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                found = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2|tuic)://[^\s]+', f.read())
                unique_configs.update(found)
                
    return unique_configs

def save_and_push(configs):
    if not os.path.exists(GITHUB_MIRROR_DIR):
        os.makedirs(GITHUB_MIRROR_DIR)

    # Сохраняем в 26.txt
    with open(FINAL_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(configs))
    
    log(f"Собрано {len(configs)} уникальных конфигов.")

    # Логика деплоя на GitHub
    try:
        subprocess.run(["git", "add", "."], check=True)
        # Брендированный коммит
        commit_msg = f"🚀 {BRAND}: Sync Database ({len(configs)} nodes)"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Данные успешно отправлены в GitHub!")
    except Exception as e:
        log(f"Git Error: {e}")

def main():
    # Запускаем сборку
    data = get_configs()
    if data:
        save_and_push(data)
    else:
        log("Конфиги не найдены, пушить нечего.")

if __name__ == "__main__":
    main()
