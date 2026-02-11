# JobPulse 🤖

**Automated monitoring and testing system for IT job platforms**

JobPulse solves two QA challenges in one ethical system:

✅ **Continuous monitoring** — detects new job postings hourly and sends Telegram alerts  
✅ **End-to-end testing** — validates demo site functionality via Playwright and PyTest

*Ethical approach:* Uses self-hosted demo site ([jobboard-demo](https://anastasiiaglushakova.github.io/jobboard-demo/)) — no scraping of third-party platforms.

---

## 🔁 Two Modes of Operation

| Mode          | How it works                                | Terminal required? |
| ------------- | ------------------------------------------- | ------------------ |
| **Monitoring**| Hourly auto-check → detects new vacancies → Telegram alerts | ❌ No (GitHub Actions) |
| **Testing**   | Interactive commands (`/start`, `/test_jobboard`) | ✅ Yes (local only) |

> 💡 Monitoring runs 24/7 in cloud. Interactive bot requires local terminal.

---

## 🔄 Monitoring Flow

```
GitHub Actions (every hour)
        ↓
Parse jobboard-demo via Playwright
        ↓
Compare against cache (jobs_cache.json)
        ↓
Send Telegram alerts for NEW vacancies only
        ↓
Update cache to avoid duplicates
```

*First run:* sends all 12 demo vacancies  
*Subsequent runs:* sends only new vacancies (smart deduplication)

---

## 🚀 Quick Start

### Prerequisites

* Python 3.10+
* Git
* Telegram account

### Setup

```bash
git clone https://github.com/anastasiiaglushakova/jobpulse-bot.git
cd jobpulse-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

### Configure Telegram Bot

1. Open Telegram → find **@BotFather**
2. Send `/newbot` → follow instructions
3. Copy the token (format: `1234567890:AAH_xxx...`)
4. Edit `.env`:

```env
TELEGRAM_BOT_TOKEN=1234567890:AAH_your_token_here
TELEGRAM_CHAT_ID=123456789
JOBSITE_URL=https://anastasiiaglushakova.github.io/jobboard-demo/
```

> 🔒 `.env` is excluded via `.gitignore` — never commit secrets.

---

## ▶ Run Components

### Run tests

```bash
pytest tests/test_jobboard.py -v
```

### Start interactive bot (local only)

```bash
python3 bot.py
```

Available commands:
* `/start` — welcome menu
* `/test_jobboard` — run job board tests
* `/status` — check site availability

### Test parser locally

```bash
python3 parser.py
```

Sends current vacancies to your Telegram chat.

---

## 🤖 Telegram Commands

| Command          | Description                              |
| ---------------- | ---------------------------------------- |
| `/start`         | Welcome message with available commands  |
| `/help`          | Project description                      |
| `/status`        | Check availability of demo sites         |
| `/test_jobboard` | Run tests for job board demo site        |
| `/test_internet` | Run tests for the-internet platform      |

---

## 📄 Example Test Report

```
✅ JobBoard Demo — Test Report
───────────────────────────────────────
Total tests:    6
Passed:         6 ✅
Failed:         0 ❌
Duration:       6.51s
───────────────────────────────────────
✅ test_page_loads                 1.23s
✅ test_search_python_jobs         1.45s
✅ test_search_qa_jobs             1.32s
✅ test_search_no_results          1.18s
✅ test_job_card_structure         1.33s
✅ test_sort_jobs                  1.81s
```

---

## ⚙️ Automation

| Workflow          | Trigger                     | Purpose                              |
| ----------------- | --------------------------- | ------------------------------------ |
| `ci.yml`          | Push / PR                   | Run e2e tests, upload reports        |
| `hourly-check.yml`| Every hour (`0 * * * *`)    | Detect new vacancies → Telegram alert|

Workflows are visible in the **Actions** tab.

---

## 🧪 Test Coverage

| Feature                  | Test                                               |
| ------------------------ | -------------------------------------------------- |
| Page load                | ✅ `test_page_loads`                                |
| Search functionality     | ✅ `test_search_python_jobs`, `test_search_qa_jobs` |
| Empty results handling   | ✅ `test_search_no_results`                         |
| DOM structure validation | ✅ `test_job_card_structure`                        |
| Sorting                  | ✅ `test_sort_jobs`                                 |
| Visual regression        | ✅ Automatic screenshots on failure                 |

All tests use **Page Object Model (POM)**.

---

## 🏗️ Project Structure

```
jobpulse-bot/
├── bot.py                     # Interactive bot (local only)
├── parser.py                  # Automated parser (GitHub Actions)
├── jobs_cache.json            # Stores seen vacancies
├── pages/
│   ├── jobboard_page.py       # POM for job board
│   └── internet_page.py       # POM for the-internet
├── tests/
│   ├── test_jobboard.py       # E2E tests for job board
│   └── test_internet_login.py # E2E tests for the-internet
├── utils/
│   ├── reporter.py            # Test report generator
│   ├── logger.py              # Custom logger
│   └── conftest_hooks.py      # PyTest hooks
├── .github/workflows/
│   ├── ci.yml                 # Test automation
│   └── hourly-check.yml       # Hourly monitoring
└── requirements.txt           # Dependencies
```

---

## ⚙️ Technologies

| Category       | Tools                     |
| -------------- | ------------------------- |
| Test Framework | PyTest, Playwright        |
| Telegram Bot   | python-telegram-bot       |
| CI/CD          | GitHub Actions            |
| HTTP Client    | requests                  |
| Logging        | loguru                    |
| Demo Site      | HTML5, CSS3, Vanilla JS   |
| Environment    | python-dotenv             |

---

## 🔒 Security Notes

* `.env` excluded via `.gitignore`
* Telegram token has no payment permissions
* Demo site contains no real user data
* No third-party platforms are scraped

---

## 📜 License

MIT License — see `LICENSE` for details.