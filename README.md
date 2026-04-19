# ☀️ Suhani's Daily Digest

A personal morning news dashboard — fetches RSS headlines across 14 categories, summarizes them with Groq AI, pulls live market data, teaches you Spanish, and emails you a condensed digest. Opens a beautiful HTML dashboard in your browser.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `digest.py` | Main script — run this every morning |
| `config.py` | Your API keys & settings (fill this in) |
| `setup.bat` | One-click Windows dependency installer |
| `dashboard.html` | Generated fresh each run (auto-opens) |

---

## ⚡ Quick Start

### Step 1 — Install dependencies
```
Double-click setup.bat
```
Or manually:
```bash
pip install feedparser requests groq
```

### Step 2 — Get your Groq API key (free)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → API Keys → Create Key
3. Paste it into `config.py` → `GROQ_API_KEY`

### Step 3 — Set up Gmail App Password
Gmail blocks direct password login for scripts. You need an **App Password**:
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Enable 2-Step Verification first if not done
3. Select "Mail" + "Windows Computer" → Generate
4. Copy the 16-character password into `config.py` → `EMAIL_APP_PASSWORD`

### Step 4 — Run it!
```bash
python digest.py
```
The dashboard opens in your browser automatically. Check your inbox for the email digest.

---

## 🕗 Schedule it (Windows Task Scheduler)

1. Open **Task Scheduler** (search in Start menu)
2. Click **"Create Basic Task"** (right panel)
3. Name: `Suhani Daily Digest`
4. Trigger: **Daily** → Start: `8:00:00 AM`
5. Action: **Start a program**
   - Program/script: `python`
   - Add arguments: `C:\path\to\news_digest\digest.py`
   - Start in: `C:\path\to\news_digest\`
6. Finish → **Enable** the task

To test: right-click the task → **Run**

To check logs: add `>> C:\path\to\news_digest\digest.log 2>&1` to arguments

---

## 📰 News Categories

| Category | Tone |
|----------|------|
| World Affairs | Sharp 25-year-old briefing |
| War & Conflicts | War correspondent — factual, grave |
| India News | Young Indian professional |
| Politics | Balanced, analytical |
| Technology | Enthusiastic tech friend |
| AI & Data Science | Data science fresher perspective |
| Science | Curious and awe-inspiring |
| Business & Finance | FT-reader energy |
| Trends & Pop Culture | Chatty friend texting you |
| Entertainment | Smart entertainment journalism |
| Wellness & Psychology | Evidence-conscious, warm |
| Lifestyle & Fashion | Industry-insider peer |
| Personal Growth & Career | Honest mentorship |
| General News | Crisp news anchor |

---

## 📊 Market Data

| Asset | Source |
|-------|--------|
| Nifty 50 | Yahoo Finance (free) |
| S&P 500 | Yahoo Finance (free) |
| Bitcoin | CoinGecko (free) |
| Ethereum | CoinGecko (free) |

---

## 🇪🇸 Spanish Lessons

15 rotating themes based on day of year:
Greetings → Numbers → Food → Travel → Work → Shopping → Family → Health → Weather → Emotions → Culture → Tech → Art → Sports → Daily Routines

Each lesson includes 5 phrases + cultural note + A1→B2 roadmap hint.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| Email not sending | Check App Password in config.py |
| RSS feed errors | Normal — some feeds go down temporarily |
| Groq API error | Verify your API key at console.groq.com |
| Market data N/A | Yahoo Finance rate limiting — retry later |
| Browser doesn't open | Manually open `dashboard.html` |

---

## 🛡️ Privacy Note

`config.py` contains your credentials. **Never share or upload it.** Add it to `.gitignore` if you use Git.

---

*Built for Suhani Khanna · Powered by Groq llama-3.3-70b-versatile*
