# AWS Polly Pricing Notes (Neural Engine)

## Overview
This document summarizes the estimated cost of using **Amazon Polly** with the **Neural engine** in production, after the initial free tier period.

---

## Assumptions
| Parameter           | Value |
|---------------------|-------|
| Annual usage        | **1,000,000 characters** |
| Engine type         | **Neural** |
| API used            | `SynthesizeSpeech` |
| AWS Region          | **us-east-1** (N. Virginia, standard pricing) |

---

## Pricing (as of Aug 2025)

**AWS official pricing**:
[Amazon Polly Pricing Page](https://aws.amazon.com/polly/pricing/)

| Engine  | Price per 1M characters | Annual cost for 1M characters |
|---------|-------------------------|--------------------------------|
| Neural  | **$16.00 USD**          | **$16.00 USD / year**          |
| Standard| $4.00 USD               | $4.00 USD / year               |

---

## Notes
- **Billing is based on characters, not words.**
  Example: "Hello" = 5 characters, not 1 word.
- In this test account, **Amazon Polly IS included in the AWS Free Tier** for the first **12 months**, with:
  - **1M characters/month (Neural)**
  - **5M characters/month (Standard)**
- After the free tier expires, Neural costs **$16 per 1M characters**.
- Costs for storing or delivering audio (e.g., **S3**, **CloudFront**) are **not included** in this calculation.

---

## Summary Table

| Annual Characters | Annual Cost (Neural) | Monthly Equivalent | Notes |
|-------------------|----------------------|--------------------|-------|
| 1,000,000         | **$16.00 USD**       | ~$1.33 USD         | After free tier ends |

---

## Related
- **Free Tier usage**: Track via [AWS Billing & Cost Management Console](https://console.aws.amazon.com/billing/home)
- **Voice list**: [Available Voices in Amazon Polly](https://docs.aws.amazon.com/polly/latest/dg/available-voices.html)
