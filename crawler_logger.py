import json
import os
from datetime import datetime

LOG_FILE = "crawl_log.json"

# Initialize log file if not present
def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

# Append a new log entry
def log_page_visit(url, load_time=None, content_size=None, total_links=None, internal_links=None, external_links=None, status="success"):
    entry = {
        "url": url,
        "timestamp": datetime.utcnow().isoformat(),
        "load_time": round(load_time, 3) if load_time else None,
        "content_size": content_size,
        "total_links": total_links,
        "internal_links": internal_links,
        "external_links": external_links,
        "status": status
    }
    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

# Clear log if needed
def clear_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

if __name__ == "__main__":
    init_log()
    log_page_visit("https://example.com", load_time=1.23, content_size=20480, total_links=12, internal_links=9, external_links=3)