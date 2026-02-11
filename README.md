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
> 💬 Bot interface is in Russian (demonstrates localization support). Core code and documentation are in English.

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
* `/test_internet` — run the-internet tests
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
─────────────────────────────────────────────
Total tests:    7
Passed:         7 ✅
Failed:         0 ❌
Duration:       7.23s
─────────────────────────────────────────────
✅ test_page_loads                    1.11s
✅ test_search_python_jobs            1.32s
✅ test_search_qa_jobs                1.22s
✅ test_search_no_results             1.22s
✅ test_job_card_structure            1.40s
✅ test_sort_jobs                     1.55s
✅ test_search_special_characters     0.89s
─────────────────────────────────────────────
Generated: 2026-02-12 18:45:22
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

| Feature                  | Tests                                                                 |
| ------------------------ | --------------------------------------------------------------------- |
| Page load                | ✅ `test_page_loads`                                                  |
| Search functionality     | ✅ `test_search_python_jobs`, `test_search_qa_jobs`                   |
| Edge cases               | ✅ `test_search_no_results`, `test_search_special_characters`         |
| DOM structure validation | ✅ `test_job_card_structure`                                          |
| Sorting                  | ✅ `test_sort_jobs`                                                   |
| Visual regression        | ✅ Automatic screenshots on failure                                   |
| Authentication           | ✅ 3 tests for the-internet login (`test_internet_login.py`)          |

All tests use **Page Object Model (POM)**.  
**Total:** 10 end-to-end tests (7 for JobBoard + 3 for the-internet).

---

## 🏗️ Project Structure

```
jobpulse-bot/
├── bot.py                     # Interactive Telegram bot (local only)
├── parser.py                  # Automated parser (GitHub Actions)
├── conftest.py                # PyTest fixtures and configuration
├── pytest.ini                 # PyTest configuration
├── pages/
│   ├── jobboard_page.py       # POM for job board demo
│   └── internet_page.py       # POM for the-internet
├── tests/
│   ├── test_jobboard.py       # 7 E2E tests for job board
│   └── test_internet_login.py # 3 E2E tests for the-internet
├── utils/
│   ├── reporter.py            # Human-readable test reports
│   ├── logger.py              # Custom logger with rotation
│   └── conftest_hooks.py      # PyTest hooks for reporting
├── .github/workflows/
│   ├── ci.yml                 # Test automation on push/PR
│   └── hourly-check.yml       # Hourly monitoring via schedule
├── requirements.txt           # Dependencies
├── .gitignore                 # Excludes artifacts (cache, logs, venv)
├── LICENSE                    # MIT License
└── README.md                  # This file
```

---

## ⚙️ Technologies

| Category       | Tools                                      |
| -------------- | ------------------------------------------ |
| Test Framework | PyTest, Playwright                         |
| Telegram Bot   | python-telegram-bot                        |
| CI/CD          | GitHub Actions                             |
| HTTP Client    | requests                                   |
| Logging        | Custom logger (not loguru — removed)       |
| Demo Site      | HTML5, CSS3, Vanilla JS (GitHub Pages)     |
| Environment    | python-dotenv                              |

---

## 🔒 Security & Ethics

* `.env` excluded via `.gitignore` — secrets never committed
* Telegram token has no payment permissions
* Demo site contains no real user data
* **No third-party platforms are scraped** — only self-hosted demo site
* Rate limits respected (1 check/hour via GitHub Actions)

---

## 📜 License

MIT License © 2026 Anastasiia Glushakova  
See `LICENSE` for details.