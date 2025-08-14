# app/amazon_polly_client.py

import json
from pathlib import Path
import boto3
import os
from dotenv import load_dotenv
from app.usage_tracker import check_and_log_polly

# Max Polly Characters Length (UTF8)
MAX_POLLY_CHAR_LENGTH = 3000


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
        if not summary:
            continue

        if len(summary) > MAX_POLLY_CHAR_LENGTH:
            print(f"⚠️ Skipping article {i} – text too long ({len(summary)} characters)")
            continue

        output_path = output_dir / f"article_{i:02}.mp3"
        print(f"Generating audio for article {i}...")

        try:
            # Synthesize speech
            response = polly.synthesize_speech(
                Text=summary,
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine=engine
            )

            # Save the audio stream to a file
            with open(output_path, "wb") as f:
                f.write(response["AudioStream"].read())

            # check and log amazan polly usage
            text_len = 500 # 100 words x 5 chars on average
            check_and_log_polly(text_len)

        except Exception as e:
            print(f"⚠️ Failed to generate audio for article {i}: {e}")

    print("✅ All summaries converted to audio.")


if __name__ == "__main__":
    # Example: Run standalone
    example_json = Path("data/daily_summary_2025-08-07.json")
    example_output_dir = Path("output/audio/2025-08-07")

    summaries_to_mp3(
        json_path=example_json,
        output_dir=example_output_dir,
        voice_id="Ruth",
        engine="neural"
    )
