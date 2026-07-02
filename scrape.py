"""
scrape.py
Calls the Apify LinkedIn Jobs Scraper and returns a list of raw job dicts.
"""

import os
import time
import requests


APIFY_TOKEN = os.environ["APIFY_API_TOKEN"]
ACTOR_ID    = "hKByXkMQaC5Qt9UMN"
BASE_URL    = "https://api.apify.com/v2"

SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=Java+Developer+Fresher&location=India&f_TPR=r86400&f_E=1&sortBy=DD&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search/?keywords=Associate+Software+Developer+Java+Spring+Boot&location=India&f_TPR=r86400&f_E=1&sortBy=DD&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search/?keywords=Software+Engineer+Java+Backend+Fresher&location=India&f_TPR=r86400&f_E=1&sortBy=DD&position=1&pageNum=0",
]


def run_scraper() -> list[dict]:
    """Trigger Apify actor, wait for completion, return job list."""

    # 1. Start the actor run
    run_resp = requests.post(
        f"{BASE_URL}/acts/{ACTOR_ID}/runs",
        params={"token": APIFY_TOKEN},
        json={
            "urls": SEARCH_URLS,
            "count": 30,
            "scrapeCompany": False,
        },
        timeout=30,
    )
    run_resp.raise_for_status()
    run_id = run_resp.json()["data"]["id"]
    print(f"[scrape] Actor run started → runId={run_id}")

    # 2. Poll until finished (max 5 minutes)
    for attempt in range(30):
        time.sleep(10)
        status_resp = requests.get(
            f"{BASE_URL}/actor-runs/{run_id}",
            params={"token": APIFY_TOKEN},
            timeout=15,
        )
        status_resp.raise_for_status()
        status = status_resp.json()["data"]["status"]
        print(f"[scrape] attempt {attempt+1}: status={status}")
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {status}")
    else:
        raise TimeoutError("Apify run did not complete within 5 minutes")

    # 3. Fetch dataset items
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    items_resp = requests.get(
        f"{BASE_URL}/datasets/{dataset_id}/items",
        params={
            "token": APIFY_TOKEN,
            "limit": 30,
            "fields": "title,companyName,location,link,postedAt,seniorityLevel,employmentType,descriptionText,applicantsCount",
        },
        timeout=30,
    )
    items_resp.raise_for_status()
    jobs = items_resp.json()
    print(f"[scrape] Retrieved {len(jobs)} jobs from dataset")
    return jobs


if __name__ == "__main__":
    import json
    jobs = run_scraper()
    print(json.dumps(jobs[:2], indent=2))
