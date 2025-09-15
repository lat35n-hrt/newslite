# app/amazon_polly_client.py

import json
from pathlib import Path
import boto3
import os
from dotenv import load_dotenv
from app.usage_tracker import check_and_log_polly
from contextlib import closing
import html

# Sanitize text for SSML
def sanitize_for_ssml(text: str) -> str:
    return html.escape(text, quote=True).replace("\n", " ")

# Max Polly Characters Length (UTF8)
MAX_POLLY_CHAR_LENGTH = 3000

def save_polly_settings(folder: Path, rate: str, engine: str, voice_id: str):
    """
    Save Polly synthesis settings into a JSON file (settings.json)
    inside the given folder.

    Args:
        folder (Path): Directory where the mp3 is stored.
        rate (str): Speech rate, e.g. "90%".
        engine (str): Polly engine, e.g. "neural".
        voice_id (str): Polly voice ID, e.g. "Ruth".
    """
    settings = {
        "rate": rate,
        "engine": engine,
        "voice_id": voice_id
    }

    settings_path = Path(folder) / "settings.json"
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Polly settings saved -> {settings_path}")

def summaries_to_mp3(
    json_path: Path,
    output_dir: Path,
    voice_id: str = "Ruth",
    engine: str = "neural"
) -> None:
    """
    Convert summaries from a JSON file to MP3 using Amazon Polly.

    Args:
        json_path (Path): Path to the JSON file containing summaries.
        output_dir (Path): Directory to save MP3 files.
        voice_id (str): Amazon Polly VoiceId (default: "Ruth").
        engine (str): Polly engine ("neural" or "standard", default: "neural").
    """
    # Load environment variables
    load_dotenv()

    # Create Polly client
    polly = boto3.client(
        "polly",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

    # Load JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each article
    for i, article in enumerate(data, 1):
        summary = article.get("summary", "").strip()
        safe_text = sanitize_for_ssml(summary)

        if not safe_text:
            continue

        if len(safe_text) > MAX_POLLY_CHAR_LENGTH:
            print(f"⚠️ Skipping article {i} – text too long ({len(safe_text)} characters)")
            continue

        rate = os.getenv("AWS_POLLY_RATE", "100%")

        # Wrap with <speak> and <prosody>
        summary_ssml = f"<speak><prosody rate='{rate}'>{safe_text}</prosody></speak>"

        output_path = output_dir / f"article_{i:02}.mp3"
        print(f"Generating audio for article {i}...")

        try:
            # Synthesize speech
            response = polly.synthesize_speech(
                # Text=summary,
                # SSML test with rate setting
                Text=summary_ssml,
                TextType="ssml",
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine=engine
            )

            # Save the audio stream to a file
            with closing(response["AudioStream"]) as stream:
                with open(output_path, "wb") as f:
                    f.write(stream.read())


            # check and log amazan polly usage
            text_len = len(summary_ssml) # Initial sample data 500: 100 words x 5 chars on average
            check_and_log_polly(text_len)

        except Exception as e:
            print(f"⚠️ Failed to generate audio for article {i}: {e}")

    print("✅ All summaries converted to audio.")

    # Add setting file in the daily directory
    save_polly_settings(output_dir, rate="90%", engine=engine, voice_id=voice_id)


if __name__ == "__main__":
    # Example: Run standalone
    example_json = Path("data/daily_summary_2025-09-14.json")
    example_output_dir = Path("output/audio/work/2025-09-14")

    # Ensure output directory exists
    example_output_dir.mkdir(parents=True, exist_ok=True)

    summaries_to_mp3(
        json_path=example_json,
        output_dir=example_output_dir,
        voice_id="Ruth",
        engine="neural"
    )
