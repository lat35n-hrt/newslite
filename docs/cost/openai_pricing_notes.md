## 💰 Token Usage and Cost Estimation
This project uses the OpenAI API (gpt-3.5-turbo) to generate daily article summaries. Since token usage varies depending on article length and response size, we track usage locally and estimate the cost based on the number of tokens consumed.

📊 Observed Daily Usage (August 2025)

| Date  | Articles (Requests) | Input Tokens | Output Tokens | Total Tokens | Avg / Request  |
| ----- | ------------------- | ------------ | ------------- | ------------ | -------------- |
| Aug 3 | 24                  | 19,450       | 2,124         | **21,574**   | \~899 tokens   |
| Aug 4 | 6                   | 7,874        | 683           | **8,557**    | \~1,426 tokens |
| Aug 5 | 6                   | 8,727        | 668           | **9,395**    | \~1,565 tokens |


Estimated average per request: ~1,300–1,400 tokens

OpenAI's price for gpt-3.5-turbo: $0.0015 per 1,000 tokens

Example cost for Aug 5: 9,395 tokens × $0.0015 / 1000 = $0.0141

📌 Cost Tracking Strategy
You can track usage in two ways:

1. Flat-rate estimation
A simple approach assuming an average number of tokens per request:

```python
check_and_log_usage(0.0005)  # Estimated cost per summary
```

2. Token-based dynamic estimation
Recommended if cost needs to be more accurate:

```python
PRICE_PER_1K_TOKEN = 0.0015  # For gpt-3.5-turbo
cost = tokens * (PRICE_PER_1K_TOKEN / 1000)
check_and_log_usage(cost)
```

🔍 Notes
The original flat estimate of $0.0005/article was based on earlier low-token samples (~900 tokens), but underestimates current usage.

Based on real-world usage, we recommend $0.0015/article or using token-based calculation.



💰 Estimated Cost per Article Summary
This project estimates the OpenAI API cost per article summary based on actual usage, rather than solely relying on theoretical pricing.

🔍 Practical Estimation (Based on Real Usage)
During development, daily summaries (6 articles) showed total usage around:

Total tokens: ~9,000

Estimated cost: $0.003–0.004 per 6 articles

→ ~$0.0005 per article, on average

This estimation matches OpenAI dashboard billing data closely (with <10% variance).

🧮 Theoretical Estimation (Based on OpenAI Pricing)
As of 2025, OpenAI pricing for gpt-3.5-turbo is:

$0.0015 / 1K input tokens

$0.0005 / 1K output tokens

A typical article is around 1,300 tokens, and summary output is less than 200 tokens.

Estimated cost per article (input only):
1300 * 0.0015 / 1000 = $0.00195

→ This is 4x higher than actual observed costs.

⚠️ Why This Gap?
Several factors may contribute:

OpenAI's billing may not be fully linear at very low usage.

Initial credits or usage caps may affect perceived cost.

Output tokens are minimal (~1/10 of input) and often negligible in real billing.

There may be internal optimizations or minimum charge thresholds not clearly documented.

✅ Recommendation
Scenario	Cost per Article	Reason
Development / Testing	$0.0005	Matches real-world billing closely. Lightweight and conservative.
Production / Budget-sensitive environments	$0.0015 or token-based	Aligns with OpenAI’s pricing model and protects against cost drift or token spikes.

We recommend starting with the practical model and adjusting as usage grows or changes.