"""
send_email.py — Fixed version
Sends the daily Excel report to recipient(s) via Gmail SMTP.
Supports multiple recipients via comma-separated RECIPIENT_EMAIL.
Fixed: removed undefined variable bug from previous version.
"""

import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from pathlib              import Path


def send_report(excel_path: str, job_summary: list[dict]) -> None:

    sender    = os.environ["GMAIL_SENDER"]
    password  = os.environ["GMAIL_APP_PASSWORD"]

    # Support multiple recipients via comma-separated string
    recipient_env = os.environ["RECIPIENT_EMAIL"]
    recipients    = [r.strip() for r in recipient_env.split(",")]

    today_str       = date.today().strftime("%B %d, %Y")
    total           = len(job_summary)
    apply_now_count = sum(1 for j in job_summary if j.get("apply_priority") == "APPLY NOW")
    fresher_count   = sum(1 for j in job_summary if j.get("is_fresher_friendly"))
    top5            = [j for j in job_summary if j.get("stars", 0) >= 4][:5]

    # Build top-5 HTML rows
    rows_html = ""
    for i, j in enumerate(top5, 1):
        bg = "#f0fff4" if i % 2 == 0 else "#ffffff"
        pc = "#1a7a1a" if j.get("apply_priority") == "APPLY NOW" else "#b35900"
        rows_html += f"""
        <tr style="background:{bg}">
          <td style="padding:8px;border:1px solid #ddd">{i}</td>
          <td style="padding:8px;border:1px solid #ddd"><b>{j.get('title','')}</b></td>
          <td style="padding:8px;border:1px solid #ddd">{j.get('company','')}</td>
          <td style="padding:8px;border:1px solid #ddd">{j.get('location','')}</td>
          <td style="padding:8px;border:1px solid #ddd;text-align:center">{j.get('star_label','')}</td>
          <td style="padding:8px;border:1px solid #ddd;color:{pc};font-weight:bold;text-align:center">
            {j.get('apply_priority','')}
          </td>
          <td style="padding:8px;border:1px solid #ddd">
            <a href="{j.get('link','#')}" style="color:#0563C1">View Job</a>
          </td>
        </tr>"""

    # Handle case where no 4-star jobs exist
    if not rows_html:
        rows_html = f"""
        <tr>
          <td colspan="7" style="padding:12px;text-align:center;color:#666">
            No strong matches today — check the Excel for all results
          </td>
        </tr>"""

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;color:#222;max-width:800px;margin:auto">

      <div style="background:#1F3864;color:#fff;padding:20px;border-radius:8px 8px 0 0">
        <h2 style="margin:0">🎯 Daily Java Job Report</h2>
        <p style="margin:4px 0;font-size:14px">{today_str} · Groq AI + Apify · Cost: ₹0</p>
      </div>

      <div style="background:#f8f9fa;padding:16px;border:1px solid #dee2e6">
        <b>Hi Balu 👋</b><br><br>
        Your daily Java job report is ready. Groq llama-3.3-70b analyzed every job
        description against your resume and ranked them for you.
        <br><br>
        <table style="border-collapse:collapse;width:100%;margin-top:8px">
          <tr>
            <td style="background:#E2EFDA;padding:12px;border-radius:6px;text-align:center;width:33%">
              <div style="font-size:24px;font-weight:bold;color:#375623">{total}</div>
              <div style="font-size:12px;color:#555">Jobs Analyzed</div>
            </td>
            <td style="width:2%"></td>
            <td style="background:#DDEBF7;padding:12px;border-radius:6px;text-align:center;width:33%">
              <div style="font-size:24px;font-weight:bold;color:#1F3864">{fresher_count}</div>
              <div style="font-size:12px;color:#555">Fresher-Friendly</div>
            </td>
            <td style="width:2%"></td>
            <td style="background:#FCE4D6;padding:12px;border-radius:6px;text-align:center;width:30%">
              <div style="font-size:24px;font-weight:bold;color:#C00000">{apply_now_count}</div>
              <div style="font-size:12px;color:#555">Apply NOW</div>
            </td>
          </tr>
        </table>
      </div>

      <h3 style="color:#1F3864;margin:20px 0 8px">🏆 Top Matches Today</h3>
      <table style="border-collapse:collapse;width:100%;font-size:13px">
        <tr style="background:#1F3864;color:#fff">
          <th style="padding:8px;border:1px solid #555">#</th>
          <th style="padding:8px;border:1px solid #555">Role</th>
          <th style="padding:8px;border:1px solid #555">Company</th>
          <th style="padding:8px;border:1px solid #555">Location</th>
          <th style="padding:8px;border:1px solid #555">Match</th>
          <th style="padding:8px;border:1px solid #555">Priority</th>
          <th style="padding:8px;border:1px solid #555">Link</th>
        </tr>
        {rows_html}
      </table>

      <div style="background:#fff8e1;border-left:4px solid #f59e0b;padding:12px;margin:20px 0;border-radius:0 6px 6px 0">
        <b>📎 Full report attached</b> — Excel file with 4 sheets:
        Top Matches · Fresher Only · Skills Gap Analysis · Action Plan
      </div>

      <div style="background:#f1f5f9;padding:12px;border-radius:6px;font-size:11px;color:#666;margin-top:16px">
        Auto-generated · Groq llama-3.3-70b + Apify LinkedIn Scraper<br>
        Runs every day at 10:00 AM IST via GitHub Actions · Cost: ₹0
      </div>

    </body></html>
    """

    # Assemble MIME message
    msg            = MIMEMultipart("mixed")
    msg["Subject"] = f"🎯 Java Jobs {today_str} | {apply_now_count} APPLY NOW · {fresher_count} Fresher Friendly"
    msg["From"]    = sender
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    # Attach Excel file
    with open(excel_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    filename = Path(excel_path).name
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    # Send via Gmail SMTP SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())

    print(f"[email] ✅ Report sent to: {', '.join(recipients)}")
