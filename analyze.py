"""
analyze.py  —  Groq Edition (FREE)
Sends scraped jobs + Balu's resume to Groq API (llama-3.3-70b).
Returns structured JSON analysis for each job.
Groq is completely free with generous rate limits.
"""

import os
import json
import requests
from pathlib import Path

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL   = "gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo", etc.
OPENAI_URL     = "https://api.openai.com/v1/chat/completions"

RESUME_TEXT  = Path("resume.txt").read_text()

SYSTEM_PROMPT = """You are a brutally honest career advisor specializing in Java backend developer roles in India.
You analyze job descriptions against a candidate's resume and return structured JSON assessments.
You never sugarcoat. You are direct, specific, and actionable.
Always respond with ONLY valid JSON array — no markdown, no preamble, no explanation outside the JSON."""

USER_PROMPT_TEMPLATE = """Here is the candidate's resume:
<resume>
{resume}
</resume>

Here are {count} job descriptions scraped from LinkedIn today. Analyze EACH job against the resume.

<jobs>
{jobs_json}
</jobs>

For EACH job, return a JSON object with exactly these fields:
- "title": job title (string)
- "company": company name (string)
- "location": location (string)
- "link": LinkedIn URL (string)
- "date_posted": date posted (string)
- "seniority": seniority level from the posting (string)
- "employment_type": full-time / internship / contract (string)
- "stars": match score 1-5 as integer (5=perfect match, 1=not suitable)
- "star_label": visual stars like "★★★★★" or "★★★☆☆" (string)
- "skills_matched": list of specific skills from the JD that the candidate HAS (list of strings)
- "skills_missing": list of specific skills from the JD that the candidate is MISSING (list of strings)
- "is_fresher_friendly": true if the job is genuinely suitable for 0-1 yr experience (boolean)
- "fresher_reason": one sentence explaining why it is or isn't fresher-friendly (string)
- "verdict": one brutally honest sentence about fit — be specific, not generic (string)
- "apply_priority": "APPLY NOW" | "STRONG CONSIDER" | "STRETCH GOAL" | "SKIP"

Return a JSON array of objects, one per job. Nothing else. No markdown.
Sort by stars descending (5 stars first)."""


def analyze_jobs(jobs: list[dict]) -> list[dict]:
    """Send jobs to Groq llama-3.3-70b in batches, get structured analysis back."""

    # Trim descriptions to avoid token overload
    slim_jobs = []
    for j in jobs:
        slim_jobs.append({
            "title":           j.get("title", ""),
            "company":         j.get("companyName", ""),
            "location":        j.get("location", ""),
            "link":            j.get("link", ""),
            "date_posted":     str(j.get("postedAt", "")),
            "seniority":       j.get("seniorityLevel", ""),
            "employment_type": j.get("employmentType", ""),
            "description":     (j.get("descriptionText") or "")[:500],  # Reduce from 800 to 500
        })

    # Process in batches of 10 jobs instead of all 30 at once
    batch_size = 10
    all_analyzed = []
    
    for batch_idx in range(0, len(slim_jobs), batch_size):
        batch = slim_jobs[batch_idx:batch_idx + batch_size]
        
        # Trim resume to first 2000 chars to save tokens
        resume_trimmed = RESUME_TEXT[:2000]
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            resume=resume_trimmed,
            count=len(batch),
            jobs_json=json.dumps(batch, indent=2),
        )

        print(f"[analyze] Sending batch {batch_idx // batch_size + 1} ({len(batch)} jobs) to Groq ...")

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       GROQ_MODEL,
                "temperature": 0.3,
                "max_tokens":  4000,  # Reduce from 8000
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
            },
            timeout=120,
        )
        response.raise_for_status()

        raw_text = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if model adds them
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            raw_text = raw_text.rsplit("```", 1)[0]

        batch_analyzed = json.loads(raw_text)
        all_analyzed.extend(batch_analyzed)
        print(f"[analyze] Batch complete. Total analyzed so far: {len(all_analyzed)}")
    
    print(f"[analyze] Groq returned analysis for {len(all_analyzed)} jobs")
    return all_analyzed


if __name__ == "__main__":
    dummy = [{
        "title": "Java Developer", "companyName": "TestCo",
        "location": "Hyderabad", "link": "https://linkedin.com",
        "postedAt": "2026-07-01", "seniorityLevel": "Entry level",
        "employmentType": "Full-time",
        "descriptionText": "We need Java Spring Boot developer, 0-1 yr exp, REST APIs, MySQL."
    }]
    result = analyze_jobs(dummy)
    print(json.dumps(result, indent=2))
