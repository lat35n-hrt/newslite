# app/summary_llm.py

import os
from dotenv import load_dotenv
from openai import OpenAI
from app.usage_tracker import check_and_log_openai


load_dotenv()

# Call OpenAI API

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

USE_DUMMY = os.getenv("USE_DUMMY_SUMMARY", "false").lower() == "true"


def summarize_article(article_text: str) -> dict:

    if USE_DUMMY:
        return {"summary": "(This is a test summary due to quota limits.)"}

    # Estimated cost per article summary (tentatively 0.01 USD)
    # 0.0005 x 6 articles 4 times = 0.012 USD (0.01 USD on Open AI server side)
    check_and_log_openai(0.0005)



    """
    Returns a ~100-word plain English summary of the given article text.
    Optimized for clarity and readability for general users (not learners).
    """
    prompt = f"""
Summarize the following news article in clear and simple English.
Keep the summary around 100 words.
Do not include vocabulary explanations.

Article:
\"\"\"
{article_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, # Standard creativity level; allows some diversity and natural rephrasing.
            max_tokens=500,  # Sufficient for long summaries.
        )

        # TODO: After verifying token average, replace fixed cost tracking with dynamic token-based calculation
        # check and log usage
        # PRICE_PER_1K_TOKEN = 0.0005 # for gpt-3.5-turbo output
        # tokens = response.usage.total_tokens
        # cost = tokens * (PRICE_PER_1K_TOKEN / 1000)
        # print(f"Tokens: {tokens}, Estimated cost: ${cost:.5f}")
        # check_and_log_usage(cost)


        result = response.choices[0].message.content.strip()
        return {"summary": result}

    except Exception as e:
        print(f"Summary error: {e}")
        return {"summary": "(Summary unavailable)"}


# Manual test (optional)
if __name__ == "__main__":
    test_article = """
    A new study shows that sea levels are rising faster than expected due to melting glaciers.
    Scientists warn that coastal cities must prepare for possible flooding in the next few decades.
    The study emphasizes the urgent need for climate action to slow down global warming.
    """

    result = summarize_article(test_article)
    print(result["summary"])