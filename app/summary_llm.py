# app/summary_llm.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_article(article_text: str) -> dict:
    prompt = f"""
You are an assistant that simplifies news articles for English learners.

Summarize the following article in simple English suitable for learners at CEFR B1 level.
Limit to around 100 words.
Avoid difficult vocabulary.
Include 3 useful English vocabulary words from the article, each with a short definition in simple English.

Article:
\"\"\"
{article_text}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # "gpt-3.5-turbo" or "gpt-4"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    result = response.choices[0].message.content.strip()
    return {"summary": result}


if __name__ == "__main__":
    test_article = """
    A new study shows that sea levels are rising faster than expected due to melting glaciers.
    Scientists warn that coastal cities must prepare for possible flooding in the next few decades.
    The study emphasizes the urgent need for climate action to slow down global warming.
    """

    result = summarize_article(test_article)
    print(result["summary"])
