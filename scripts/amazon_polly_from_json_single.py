# amazon_polly_from_json_single.py

import json
from pathlib import Path
import html
import boto3
import os
from dotenv import load_dotenv
from contextlib import closing

# Sanitize text for SSML
def sanitize_for_ssml(text: str) -> str:
    safe = html.escape(text, quote=True).replace("\n", " ")
    return f"<speak>{safe}</speak>"

# Load environment variables from .env
load_dotenv()

# Create Polly client
polly = boto3.client(
    "polly",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# Joson path and output directory
json_path = Path("data/daily_summary_2025-09-12.json")
output_dir = Path("output/audio/work/2025-09-12")
output_dir.mkdir(parents=True, exist_ok=True)

# Load JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Narrator
# https://docs.aws.amazon.com/polly/latest/dg/available-voices.html
# voice_id = "Ruth" # Female + US English (Ruth and Joanna)
# Set voice id in .env

# Max Polly Charracters Length (UTF8)
MAX_POLLY_CHAR_LENGTH = 3000

# Text-to-mp3 for each article
for i, article in enumerate(data, 1):
    summary = article.get("summary", "").strip()
    summary_ssml = sanitize_for_ssml(summary)

    if not summary_ssml:
        continue

    if len(summary_ssml) > MAX_POLLY_CHAR_LENGTH:
        print(f"⚠️ Skipping article {i} - text too long ({len(summary_ssml)} characters)")
        continue

    output_path = output_dir / f"article_{i:02}.mp3"

    print(f"Generating audio for article {i}...")

    try:
        # Synthesize speech
        response = polly.synthesize_speech(
            TextType="ssml",
            Text=summary_ssml,
            OutputFormat="mp3",
            VoiceId=os.getenv("AWS_POLLY_VOICE_ID", "Ruth"),
            Engine=os.getenv("AWS_POLLY_ENGINE", "neural")
        )

        # Save the audio stream to a file
        # with open(output_path, "wb") as f:
        #     f.write(response["AudioStream"].read())

        with closing(response["AudioStream"]) as stream:
            with open(output_path, "wb") as f:
                f.write(stream.read())

    except Exception as e:
        print(f"⚠️ Failed to generate audio for article {i}: {e}")

print("✅ All summaries converted to audio.")