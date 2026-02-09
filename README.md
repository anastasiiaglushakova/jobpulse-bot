# JobPulse Bot 🤖

**Telegram bot for automated end-to-end testing of job board demo sites.**
Part of **JobPulse** — a monitoring system for IT job platforms.

---

## 🎯 Purpose

JobPulse solves a real QA challenge: continuous monitoring of job platforms without violating terms of service.

Instead of scraping commercial sites (hh.ru, etc.), this project:

* ✅ Uses a self-hosted demo site (`jobboard-demo`) deployed on GitHub Pages
* ✅ Runs real browser tests with Playwright
* ✅ Delivers human-readable reports via Telegram
* ✅ Provides screenshots on failure for fast debugging

Full testing lifecycle in one system:

```
setup → execution → reporting → diagnostics → CI/CD
```

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

### Run Tests

```bash
pytest tests/test_jobboard.py -v
```

### Start Bot

```bash
python3 bot.py
```

Then message your bot in Telegram.

---

## 🤖 Telegram Commands

| Command          | Description                                |
| ---------------- | ------------------------------------------ |
| `/start`         | Welcome message with available commands    |
| `/help`          | Project description and technologies used  |
| `/status`        | Check availability of demo job board       |
| `/test_jobboard` | Run full E2E test suite and receive report |

---

## 📄 Example Report

```
✅ JobBoard Demo — Тестовый отчёт
───────────────────────────────────────
Всего тестов:   5
Успешно:       5 ✅
Упало:         0 ❌
Время:         6.51 сек
───────────────────────────────────────
✅ test_page_loads                 1.23с
✅ test_search_python_jobs         1.45с
✅ test_search_qa_jobs             1.32с
✅ test_search_no_results          1.18с
✅ test_job_card_structure         1.33с
```

---

## 🧪 Test Coverage

| Feature                  | Test                                               |
| ------------------------ | -------------------------------------------------- |
| Page load                | ✅ `test_page_loads`                                |
| Search functionality     | ✅ `test_search_python_jobs`, `test_search_qa_jobs` |
| Empty results handling   | ✅ `test_search_no_results`                         |
| DOM structure validation | ✅ `test_job_card_structure`                        |
| Visual regression        | ✅ Automatic screenshots on failure                 |

All tests use **Page Object Model (POM)** for maintainability.

---

## 🏗️ Project Structure

```
jobpulse-bot/
├── bot.py
├── pages/
│   └── jobboard_page.py
├── tests/
│   └── test_jobboard.py
├── utils/
│   ├── reporter.py
│   ├── logger.py
│   └── conftest_hooks.py
└── .github/workflows/
    └── ci.yml
```

---

## ⚙️ Technologies

| Category       | Tools                                  |
| -------------- | -------------------------------------- |
| Test Framework | PyTest, Playwright                     |
| Telegram Bot   | python-telegram-bot                    |
| CI/CD          | GitHub Actions                         |
| Logging        | Custom logger with file rotation       |
| Demo Site      | HTML5, CSS3, Vanilla JS (GitHub Pages) |
| Environment    | python-dotenv                          |

---

## 📊 Why This Project Stands Out

| Typical Pet Project               | JobPulse Approach                        |
| --------------------------------- | ---------------------------------------- |
| Tests random public sites (risky) | ✅ Ethical: self-hosted demo site         |
| Raw test output                   | ✅ User-friendly reports with stats       |
| No failure diagnostics            | ✅ Automatic screenshots on failure       |
| Manual execution                  | ✅ Telegram-triggered automation          |
| No CI/CD                          | ✅ GitHub Actions pipeline with artifacts |

---

## 🔒 Security Notes

* `.env` is excluded via `.gitignore`
* Telegram token has no payment permissions
* Demo site contains no real user data

---

## 📜 License

MIT License — see `LICENSE` for details.

---

## 💡 For Recruiters

This project demonstrates a complete QA automation cycle — from **test design (POM)** to **execution (Playwright)** to **reporting (Telegram)** to **CI/CD (GitHub Actions)**.

Production-ready architecture with ethical testing practices.
