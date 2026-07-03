"""
analyze.py  —  Groq Edition (FREE) - Fixed Rate Limit Version
Sends scraped jobs + Balu's resume to Groq API (llama-3.3-70b).
Fixes:
  - Sends ALL 30 jobs in ONE request (not batches) to avoid rate limits
  - Trims job descriptions to 400 chars to stay under token limit
  - Longer retry waits with exponential backoff
  - Falls back to basic scoring if Groq fails
"""

import os
import json
import time
import requests
from pathlib import Path

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL   = "gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo", etc.
OPENAI_URL     = "https://api.openai.com/v1/chat/completions"

RESUME_TEXT  = Path("resume.txt").read_text()

SYSTEM_PROMPT = """You are a brutally honest career advisor for Java backend developer roles in India.
Analyze job descriptions against a candidate resume and return ONLY a valid JSON array.
No markdown, no preamble, no explanation — just the raw JSON array."""

USER_PROMPT_TEMPLATE = """Candidate resume:
{resume}

Analyze ALL {count} jobs below and return a JSON array with one object per job.

Jobs:
{jobs_json}

Each object must have exactly these fields:
- "title": string
- "company": string  
- "location": string
- "link": string
- "date_posted": string
- "seniority": string
- "employment_type": string
- "stars": integer 1-5 (5=perfect match for this fresher candidate)
- "star_label": string like "★★★★★"
- "skills_matched": list of strings (skills candidate HAS)
- "skills_missing": list of strings (skills candidate is MISSING)
- "is_fresher_friendly": boolean
- "fresher_reason": string (one sentence)
- "verdict": string (one brutally honest sentence)
- "apply_priority": one of "APPLY NOW" | "STRONG CONSIDER" | "STRETCH GOAL" | "SKIP"

Sort by stars descending. Return ONLY the JSON array, nothing else."""


def _fallback_entry(job: dict) -> dict:
    """Basic fallback when Groq is unavailable."""
    desc = (job.get("descriptionText") or "").lower()
    has_spring  = "spring" in desc or "spring boot" in desc
    has_java    = "java" in desc
    is_fresher  = any(w in desc for w in ["fresher", "0-1", "entry level", "intern", "graduate"])
    stars = 3 if (has_java and has_spring) else 2 if has_java else 1
    if is_fresher: stars = min(5, stars + 1)
    return {
        "title":             job.get("title", ""),
        "company":           job.get("companyName", ""),
        "location":          job.get("location", ""),
        "link":              job.get("link", ""),
        "date_posted":       str(job.get("postedAt", "")),
        "seniority":         job.get("seniorityLevel", ""),
        "employment_type":   job.get("employmentType", ""),
        "stars":             stars,
        "star_label":        "★" * stars + "☆" * (5 - stars),
        "skills_matched":    ["Java", "Spring Boot"] if has_spring else ["Java"] if has_java else [],
        "skills_missing":    ["Microservices", "Docker", "Kafka"],
        "is_fresher_friendly": is_fresher,
        "fresher_reason":    "Fresher keywords detected." if is_fresher else "Experience required.",
        "verdict":           "Groq analysis unavailable — basic keyword match used.",
        "apply_priority":    "STRONG CONSIDER" if stars >= 4 else "STRETCH GOAL" if stars == 3 else "SKIP",
    }


def analyze_jobs(jobs: list[dict]) -> list[dict]:
    """Send ALL jobs to Groq in one request. Falls back gracefully on rate limit."""

    # Trim descriptions aggressively — 400 chars is plenty for matching
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
            "description":     (j.get("descriptionText") or "")[:400],
        })

    prompt = USER_PROMPT_TEMPLATE.format(
        resume=RESUME_TEXT,
        count=len(slim_jobs),
        jobs_json=json.dumps(slim_jobs, indent=1),
    )

    print(f"[analyze] Sending all {len(slim_jobs)} jobs to Groq ({GROQ_MODEL}) in one request ...")

    # Exponential backoff: wait 15s, 30s, 60s between retries
    wait_times = [15, 30, 60]

    for attempt, wait in enumerate(wait_times, 1):
        try:
            response = requests.post(
                OPENAI_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       OPENAI_MODEL,
                    "temperature": 0.2,
                    "max_tokens":  8000,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt},
                    ],
                },
                timeout=120,
            )

            if response.status_code == 429:
                print(f"[analyze] ⚠️  Rate limited (429). Waiting {wait}s before retry {attempt}/{len(wait_times)} ...")
                time.sleep(wait)
                continue

            response.raise_for_status()

            raw = response.json()["choices"][0]["message"]["content"].strip()

            # Strip markdown fences if model adds them
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                raw = raw.rsplit("```", 1)[0].strip()

            analyzed = json.loads(raw)
            print(f"[analyze] ✅ Groq returned analysis for {len(analyzed)} jobs")
            return analyzed

        except json.JSONDecodeError as e:
            print(f"[analyze] ⚠️  JSON parse error on attempt {attempt}: {e}")
            if attempt < len(wait_times):
                time.sleep(wait)
            continue

        except Exception as e:
            print(f"[analyze] ⚠️  Error on attempt {attempt}: {e}")
            if attempt < len(wait_times):
                time.sleep(wait)
            continue

    # All retries failed — use keyword fallback for all jobs
    print(f"[analyze] ❌ Groq unavailable after {len(wait_times)} attempts. Using keyword fallback for all jobs.")
    results = [_fallback_entry(j) for j in jobs]
    results.sort(key=lambda x: x["stars"], reverse=True)
    return results


if __name__ == "__main__":
    dummy = [{
        "title": "Java Developer", "companyName": "TestCo",
        "location": "Hyderabad", "link": "https://linkedin.com",
        "postedAt": "2026-07-03", "seniorityLevel": "Entry level",
        "employmentType": "Full-time",
        "descriptionText": "We need Java Spring Boot developer, 0-1 yr exp, REST APIs, MySQL."
    }]
    result = analyze_jobs(dummy)
    print(json.dumps(result, indent=2))
