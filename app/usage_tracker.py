# data/usage_tracker.json
# {"total_cost_usd": 2.14, "last_reset": "2025-07-01"}

import os
import json
from datetime import datetime

USAGE_FILE = "data/usage_tracker.json"
MONTHLY_LIMIT = 3.0  # USD

def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"total_cost_usd": 0.0, "last_reset": datetime.now().strftime("%Y-%m-%d")}
    with open(USAGE_FILE) as f:
        return json.load(f)

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

def check_and_log_usage(estimated_cost_usd):
    usage = load_usage()
    now = datetime.now()

    # 月初でリセット
    if usage["last_reset"][:7] != now.strftime("%Y-%m"):
        usage = {"total_cost_usd": 0.0, "last_reset": now.strftime("%Y-%m-%d")}

    new_total = usage["total_cost_usd"] + estimated_cost_usd
    if new_total > MONTHLY_LIMIT:
        raise Exception("Monthly OpenAI API budget exceeded")

    usage["total_cost_usd"] = new_total
    save_usage(usage)
