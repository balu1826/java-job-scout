"""
main.py
Orchestrates the full daily pipeline:
  1. Scrape LinkedIn via Apify
  2. Analyze jobs via Claude API
  3. Generate Excel report
  4. Send email with attachment
"""

import sys
from datetime import date
from scrape         import run_scraper
from analyze        import analyze_jobs
from generate_excel import generate
from send_email     import send_report


def main():
    today = date.today().strftime("%Y-%m-%d")
    excel_path = f"daily_jobs_{today}.xlsx"

    print("=" * 55)
    print(f"  Java Job Scout — {today}")
    print("=" * 55)

    # Step 1: Scrape
    print("\n📡 Step 1: Scraping LinkedIn via Apify ...")
    raw_jobs = run_scraper()
    print(f"    → {len(raw_jobs)} raw jobs fetched")

    if not raw_jobs:
        print("⚠️  No jobs found today. Exiting.")
        sys.exit(0)

    # Step 2: Analyze with Claude
    print("\n🤖 Step 2: Claude is analyzing every job ...")
    analyzed = analyze_jobs(raw_jobs)
    print(f"    → {len(analyzed)} jobs analyzed and scored")

    # Step 3: Generate Excel
    print("\n📊 Step 3: Generating Excel report ...")
    generate(analyzed, excel_path)
    print(f"    → Report saved: {excel_path}")

    # Step 4: Send Email
    print("\n📧 Step 4: Sending email ...")
    send_report(excel_path, analyzed)

    print("\n✅ All done! Check your inbox.")
    print("=" * 55)


if __name__ == "__main__":
    main()
