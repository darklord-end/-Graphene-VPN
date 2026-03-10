import os
import hashlib

# --- ГЕНЕРАЦИЯ СКРЫТОГО ПУТИ ---
# Скрипт берет ключ из GitHub Secrets. Если его нет (локально), ставит дефолт.
raw_key = os.getenv("PREMIUM_KEY", "default_local_key")
# Делаем хэш, чтобы даже по названию файла нельзя было понять пароль
secure_hash = hashlib.sha256(raw_key.encode()).hexdigest()[:20]

DIR = "githubmirror"
# Теперь твой премиум файл будет называться типа 7a8b9c1d2e3f4g5h6j7k.txt
PREM_FILE = f"{DIR}/{secure_hash}.txt"
FREE_FILE = f"{DIR}/26.txt"
