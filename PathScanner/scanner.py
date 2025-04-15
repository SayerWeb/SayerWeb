import requests
import threading
from queue import Queue
import argparse
import random

# إعداد الأداة عبر سطر الأوامر
parser = argparse.ArgumentParser(description="Advanced Web Path Scanner")
parser.add_argument("-u", "--url", required=True, help="Target base URL (e.g. http://example.com)")
parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
parser.add_argument("-t", "--threads", type=int, default=20, help="Number of threads")
parser.add_argument("--proxy", help="HTTP proxy (e.g. http://127.0.0.1:8080)")
parser.add_argument("--output", help="File to save valid paths")
parser.add_argument("--user-agent", help="Custom User-Agent")
args = parser.parse_args()

# الإعدادات العامة
TARGET_URL = args.url.rstrip("/")
WORDLIST_FILE = args.wordlist
THREAD_COUNT = args.threads
PROXY = {"http": args.proxy, "https": args.proxy} if args.proxy else None
OUTPUT_FILE = args.output
USER_AGENT = args.user_agent or f"PathScanner/1.0 (Random-UA-{random.randint(1000,9999)})"

HEADERS = {
    "User-Agent": USER_AGENT
}

# قائمة الانتظار للمسارات
queue = Queue()

# تحميل المسارات
with open(WORDLIST_FILE, 'r', encoding='utf-8', errors='ignore') as file:
    for line in file:
        path = line.strip()
        if path:
            queue.put(path)

# قائمة لحفظ النتائج
found_paths = []

def scan_path():
    while not queue.empty():
        path = queue.get()
        url = f"{TARGET_URL}/{path}"
        try:
            response = requests.get(url, headers=HEADERS, proxies=PROXY, timeout=5, allow_redirects=True)
            if response.status_code in [200, 301, 302]:
                result = f"[+] Found ({response.status_code}): {url}"
                print(result)
                found_paths.append(result)
        except requests.RequestException:
            pass
        queue.task_done()

# إنشاء الخيوط
threads = []
for _ in range(THREAD_COUNT):
    thread = threading.Thread(target=scan_path)
    thread.start()
    threads.append(thread)

# انتظار انتهاء الخيوط
for thread in threads:
    thread.join()

# حفظ النتائج إن وُجد ملف إخراج
if OUTPUT_FILE:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(found_paths))
    print(f"\n[✓] Results saved to {OUTPUT_FILE}")
else:
    print("\n[✓] Scan completed.")
