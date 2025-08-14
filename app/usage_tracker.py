# data/usage_tracker.json
# {"openai_total_usd": 0.003, "polly_total_chars": 3000, "last_reset": "2025-08"}

import os
import json
from datetime import datetime
from pathlib import Path

USAGE_FILE = Path("data/usage_tracker.json")
USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

OPENAI_MONTHLY_LIMIT_USD = float(os.getenv("OPENAI_MONTHLY_LIMIT_USD", "3.0"))
POLLY_MONTHLY_LIMIT_CHARS = int(os.getenv("POLLY_MONTHLY_LIMIT_CHARS", "1000000")) # 1000000 for free charge max in 12 months of creating an account

# Initialization
def _init_usage():
    return {
        "openai_total_usd": 0.0,
        "polly_total_chars": 0,
        "last_reset": datetime.now().strftime("%Y-%m") # Reset monthly
    }

# Loading usage
def load_usage():
    # init
    if not USAGE_FILE.exists():
        usage = _init_usage()
        save_usage(usage)
        return usage

    with open(USAGE_FILE) as f:
        return json.load(f)

    # usage["last_reset"] holds the most recent reset month (i.e., the month currently being tracked)
    # The name "last_reset" may be somewhat misleading intuitively, but it currently refers to this month's data
    current_month = datetime.now().strftime("%Y-%m")
    if usage.get("last_reset") != current_month:
        usage = _init_usage()
        save_usage(usage)
    return usage


def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

def check_and_log_openai (estimated_cost_usd: float):
    usage = load_usage()
    new_total = usage["openai_total_usd"] + estimated_cost_usd

    if new_total > OPENAI_MONTHLY_LIMIT_USD:
        raise Exception("Monthly OpenAI API budget exceeded")

    usage["openai_total_usd"] = new_total
    save_usage(usage)

def check_and_log_polly(chars: int):
    usage = load_usage()
    new_total = usage["polly_total_chars"] + chars

    if new_total > POLLY_MONTHLY_LIMIT_CHARS:
        raise Exception(f"Polly monthly char limit exceeded")

    usage["polly_total_chars"] = new_total
    save_usage(usage)