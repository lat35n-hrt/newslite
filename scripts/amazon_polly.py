import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create Polly client
polly = boto3.client(
    "polly",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# Synthesize speech
response = polly.synthesize_speech(
    Text="Hello! This is a test from Amazon Polly.",
    OutputFormat="mp3",
    VoiceId="Ruth", # https://docs.aws.amazon.com/polly/latest/dg/available-voices.html
    Engine="neural"
)

# Save the audio stream to a file
with open("output.mp3", "wb") as f:
    f.write(response["AudioStream"].read())

print("✅ MP3 file saved as output.mp3")