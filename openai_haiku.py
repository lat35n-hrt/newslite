import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
  api_key=API_KEY
)

response = client.responses.create(
  model="gpt-4o-mini",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text)