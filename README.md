# 🎯 Java Job Scout v2 — 100% Free, Fully Automated

Scrapes LinkedIn for fresh Java fresher jobs **every day at 10 AM IST**,
analyzes them with **Groq llama-3.3-70b (FREE)**, generates a 4-sheet Excel,
and **emails it to you** — zero cost, forever.

---

## 💰 Total Cost: ₹0

| Service | Free Tier | Our Usage |
|---|---|---|
| GitHub Actions | 2000 min/month free | ~3 min/day = 90 min/month ✅ |
| Apify | $5 free credits/month | ~$0.93/month ✅ |
| Groq API | Free, no card needed | ~50K tokens/day ✅ |
| Gmail SMTP | Free | 1 email/day ✅ |
| **Total** | | **₹0** |

---

## 📁 Project Structure

```
java-job-scout-v2/
│
├── 📂 GitHub Actions Setup (Option A)
│   ├── resume.txt
│   ├── scrape.py
│   ├── analyze.py            ← Groq version (FREE)
│   ├── generate_excel.py
│   ├── send_email.py
│   ├── main.py
│   ├── requirements.txt
│   └── .github/
│       └── workflows/
│           └── daily_jobs.yml
│
└── 📂 apify_actor/ (Option B)
    ├── main.py               ← All-in-one Apify Actor
    ├── Dockerfile
    └── .actor/
        ├── actor.json
        └── input_schema.json
```

---

## 🔑 Get Your Free API Keys (Do This First)

### 1. Groq API Key (FREE — no card, no limits)
1. Go to **https://console.groq.com**
2. Sign up / Log in (Google login works)
3. Click **API Keys → Create API Key**
4. Copy it → looks like `gsk_xxxxxxxxxxxxxxxxxxxxxxxx`

### 2. Apify API Token (FREE tier)
1. Go to **https://console.apify.com**
2. Sign up / Log in
3. Click profile icon → **Settings → Integrations**
4. Copy your **Personal API token**

### 3. Gmail App Password (FREE)
1. Go to **https://myaccount.google.com/security**
2. Enable **2-Step Verification** if not already ON
3. Search **"App passwords"** → click it
4. App: **Mail** · Device: **Other** → type `Job Scout` → **Generate**
5. Copy the 16-character password (e.g. `abcd efgh ijkl mnop`)
6. Remove spaces → `abcdefghijklmnop` ← this is your app password

---

# 🅰️ Option A — GitHub Actions Setup

**Best for:** Set it and forget it. Runs on GitHub's cloud, no Apify dashboard needed.

## Step 1 — Create GitHub Repository
1. Go to **https://github.com → New repository**
2. Name: `java-job-scout`
3. Visibility: **Private**
4. Click **Create repository**

## Step 2 — Upload Files
Upload these files from the zip (maintain folder structure):
```
resume.txt
scrape.py
analyze.py
generate_excel.py
send_email.py
main.py
requirements.txt
.github/workflows/daily_jobs.yml   ← Important: keep this exact path
```

**Via GitHub UI:**
- For regular files: **Add file → Upload files** → drag and drop
- For `.github/workflows/daily_jobs.yml`:
  - Click **Create new file**
  - Type `.github/workflows/daily_jobs.yml` in the filename box
  - Paste the file content
  - Click **Commit new file**

**Via Git CLI:**
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/java-job-scout.git
git add .
git commit -m "Java Job Scout v2 - Groq Edition"
git push -u origin main
```

## Step 3 — Add GitHub Secrets
Go to: **Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these 5 secrets:

| Secret Name | Value |
|---|---|
| `APIFY_API_TOKEN` | Your Apify personal API token |
| `GROQ_API_KEY` | Your Groq API key (`gsk_...`) |
| `GMAIL_SENDER` | Your Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-char app password (no spaces) |
| `RECIPIENT_EMAIL` | `balubattula1826@gmail.com` |

## Step 4 — Test It Right Now
1. Go to your repo → **Actions** tab
2. Click **🎯 Daily Java Job Scout (FREE)** in the left sidebar
3. Click **Run workflow → Run workflow** (green button)
4. Watch it run live (~2-3 minutes)
5. Check your inbox!

## Step 5 — Done! 🎉
From now on GitHub runs it **every day at 10:00 AM IST automatically.**

---

# 🅱️ Option B — Apify Actor Setup

**Best for:** Everything in one place on Apify. No GitHub needed. Visual dashboard.

## Step 1 — Create a New Actor on Apify
1. Go to **https://console.apify.com**
2. Click **Actors → Create new** (top right)
3. Click **"Start from scratch"**
4. Name it: `java-job-scout`
5. Click **Create**

## Step 2 — Upload Actor Files
You'll see a file editor. Upload/paste these files from the `apify_actor/` folder:

| File | Where to put it |
|---|---|
| `main.py` | Root of actor |
| `Dockerfile` | Root of actor |
| `.actor/actor.json` | Create `.actor/` folder, add `actor.json` |
| `.actor/input_schema.json` | Same `.actor/` folder |

**Tip:** In Apify's editor, click the **+** button to create files/folders.

## Step 3 — Build the Actor
1. Click **Build** (top right in the actor editor)
2. Wait for build to complete (~1-2 minutes)
3. You'll see **"Build succeeded"** in green

## Step 4 — Fill In Your Secrets (Input)
1. Click the **Input** tab
2. Fill in all 5 fields:
   - **Apify API Token** → your token
   - **Groq API Key** → `gsk_...`
   - **Gmail Sender** → your Gmail
   - **Gmail App Password** → 16-char password
   - **Recipient Email** → `balubattula1826@gmail.com`
3. Click **Save input**

## Step 5 — Test It
Click **▶ Start** → watch the logs → check your inbox

## Step 6 — Schedule It at 10 AM IST
1. Click **Schedules** tab (left sidebar) → **Create schedule**
2. Actor: `java-job-scout`
3. Cron expression: `30 4 * * *` (= 10:00 AM IST)
4. Click **Save**

## Step 7 — Done! 🎉
Apify runs it every day at 10 AM IST. You get the email automatically.

---

## 🔧 Customization

### Change the job search
Edit `SEARCH_URLS` in `scrape.py` (GitHub) or `main.py` (Apify actor):
```python
# Add more roles or locations
SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=Java+Developer+Fresher&location=Hyderabad...",
    "https://www.linkedin.com/jobs/search/?keywords=Spring+Boot+Developer+Fresher&location=India...",
]
```

### Update your resume
Edit `resume.txt` — Groq will use the updated version on the next run.

### Change the time
```yaml
# .github/workflows/daily_jobs.yml
# IST = UTC + 5:30
# 10:00 AM IST = 04:30 UTC
- cron: "30 4 * * *"

# 08:00 AM IST = 02:30 UTC
- cron: "30 2 * * *"

# 06:00 PM IST = 12:30 UTC
- cron: "30 12 * * *"
```

---

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| No email received | Check spam folder; verify `GMAIL_APP_PASSWORD` is correct (no spaces) |
| Groq error | Check your key at console.groq.com; make sure it starts with `gsk_` |
| Apify scraper fails | Check your Apify credits (should be within free $5/month) |
| 0 jobs found | LinkedIn may have rate-limited — try again next day |
| GitHub Actions not running | Go to Actions tab → enable workflows if prompted |
| Gmail "less secure" error | You must use App Password, NOT your real Gmail password |

---

## 📧 What You'll Receive Daily

**Subject:** `🎯 Java Jobs July 02, 2026 | 3 APPLY NOW · 8 Fresher Friendly`

**Attached Excel (4 sheets):**
- **Top Job Matches** — all 20-30 jobs color-coded by match score
- **Fresher Only 🟢** — only genuinely entry-level jobs
- **Skills Gap 🔴** — what today's market wants that you're missing
- **Summary & Plan** — top 5 picks + action items for the day

---

*Built with ❤️ using Groq llama-3.3-70b + Apify + GitHub Actions — Total cost: ₹0*
