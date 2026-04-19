#!/usr/bin/env python3
"""
Suhani's Daily Digest
Fetches RSS feeds, market data, summarizes with Groq AI,
builds a beautiful HTML dashboard, and emails a condensed digest.
"""

import os
import sys
import json
import webbrowser
import smtplib
import feedparser
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from pathlib import Path
from config import (
    GROQ_API_KEY, EMAIL_ADDRESS, EMAIL_APP_PASSWORD,
    RECIPIENT_EMAIL, RECIPIENT_PHONE_EMAIL, YOUR_NAME
)

# ── RSS Feeds ────────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "World Affairs": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ],
    "War & Conflicts": [
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    "India News": [
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://www.thehindu.com/news/national/feeder/default.rss",
    ],
    "Politics": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
    ],
    "Technology": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
    ],
    "AI & Data Science": [
        "https://venturebeat.com/feed/",
        "https://towardsdatascience.com/feed",
    ],
    "Science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    ],
    "Business & Finance": [
        "https://feeds.feedburner.com/entrepreneur/latest",
        "https://www.moneycontrol.com/rss/business.xml",
    ],
    "Trends & Pop Culture": [
        "https://www.buzzfeed.com/index.xml",
        "https://pitchfork.com/rss/news/feed.xml",
    ],
    "Entertainment": [
        "https://variety.com/feed/",
        "https://deadline.com/feed/",
    ],
    "Wellness & Psychology": [
        "https://www.psychologytoday.com/us/front-page/feed",
        "https://feeds.feedburner.com/MindBodyGreen",
    ],
    "Lifestyle & Fashion": [
        "https://www.vogue.com/feed/rss",
        "https://feeds.feedburner.com/refinery29/lifestyle",
    ],
    "Personal Growth & Career": [
        "https://hbr.org/stories.rss",
        "https://feeds.feedburner.com/FastCompany",
    ],
    "General News": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    ],
}

# ── Category tone instructions for Groq ─────────────────────────────────────
TONE_INSTRUCTIONS = {
    "World Affairs": "You're briefing a sharp, globally-aware 25-year-old. Be clear, context-rich, and sophisticated. No fluff.",
    "War & Conflicts": "Deliver this like a seasoned war correspondent — factual, grave, and precise. Avoid sensationalism.",
    "India News": "Write for a young Indian professional who cares about their country's trajectory. Grounded, clear, slightly personal.",
    "Politics": "Write for someone politically curious but not partisan. Balanced, analytical, a little dry.",
    "Technology": "You're a knowledgeable tech friend explaining things over coffee. Enthusiastic but not breathless.",
    "AI & Data Science": "Write for a data science fresher who's hungry to learn. Connect developments to real implications.",
    "Science": "Curious and awe-inspiring tone. Make science feel like it matters to daily life.",
    "Business & Finance": "Sharp, practical. Like a smart friend who reads FT every morning. No jargon without explanation.",
    "Trends & Pop Culture": "Conversational, slightly cheeky. Like you're texting a friend: 'have you heard about this?'",
    "Entertainment": "Fun, light, gossip-adjacent but not trashy. Think smart entertainment journalism.",
    "Wellness & Psychology": "Warm and evidence-conscious. Like a friend who's done the research so you don't have to.",
    "Lifestyle & Fashion": "Peer-to-peer, industry-insider energy. You're talking to someone who knows the space.",
    "Personal Growth & Career": "Motivating but honest. No toxic positivity. Real, actionable, mentorship-y.",
    "General News": "Crisp news anchor energy. Neutral, clear, fast.",
}

# ── Spanish lesson themes (rotating through 15 themes by day of year) ────────
SPANISH_THEMES = [
    "Greetings & Introductions",
    "Numbers & Time",
    "Food & Dining",
    "Travel & Directions",
    "Work & Career",
    "Shopping & Money",
    "Family & Relationships",
    "Health & Body",
    "Weather & Nature",
    "Emotions & Feelings",
    "Culture & Celebrations",
    "Technology & Social Media",
    "Art & Music",
    "Sports & Fitness",
    "Daily Routines",
]

def get_spanish_theme():
    day_of_year = datetime.now().timetuple().tm_yday
    return SPANISH_THEMES[day_of_year % len(SPANISH_THEMES)]

def fetch_rss_headlines(feeds, max_per_feed=4):
    headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                # Strip HTML tags roughly
                import re
                summary = re.sub('<[^<]+?>', '', summary)[:300]
                if title:
                    headlines.append(f"• {title}: {summary}")
        except Exception as e:
            print(f"  [RSS error] {url}: {e}")
    return headlines[:10]  # cap at 10 headlines per category

def fetch_market_data():
    market = {}
    # Yahoo Finance for Nifty 50 & S&P 500
    headers = {"User-Agent": "Mozilla/5.0"}
    symbols = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC"}
    for name, symbol in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            r = requests.get(url, headers=headers, timeout=8)
            data = r.json()
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            prev = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
            change = ((price - prev) / prev) * 100
            market[name] = {"price": f"{price:,.2f}", "change": f"{change:+.2f}%"}
        except Exception as e:
            market[name] = {"price": "N/A", "change": ""}
            print(f"  [Market error] {name}: {e}")

    # CoinGecko for crypto
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=8)
        data = r.json()
        btc = data["bitcoin"]
        eth = data["ethereum"]
        market["Bitcoin"] = {"price": f"${btc['usd']:,.0f}", "change": f"{btc['usd_24h_change']:+.2f}%"}
        market["Ethereum"] = {"price": f"${eth['usd']:,.0f}", "change": f"{eth['usd_24h_change']:+.2f}%"}
    except Exception as e:
        market["Bitcoin"] = {"price": "N/A", "change": ""}
        market["Ethereum"] = {"price": "N/A", "change": ""}
        print(f"  [Crypto error]: {e}")

    return market

def summarize_with_groq(client, category, headlines, tone):
    if not headlines:
        return f"No headlines available for {category} today."
    joined = "\n".join(headlines)
    prompt = f"""You are writing a daily news digest section for "{category}".

Tone instruction: {tone}

Here are today's headlines and snippets:
{joined}

Write a tight, engaging 3–5 sentence summary of what's happening in this space today. 
Do NOT use bullet points. Write in flowing prose. Be opinionated but fair. 
End with one sentence that tells the reader why this matters or what to watch."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [Groq error] {category}: {e}")
        return f"Summary unavailable for {category} today. ({e})"

def generate_spanish_lesson(client, theme):
    prompt = f"""Generate a Spanish language lesson on the theme: "{theme}".

Format your response as valid JSON only, no markdown, like this:
{{
  "theme": "{theme}",
  "intro": "One warm sentence about this theme in language learning",
  "phrases": [
    {{"spanish": "...", "english": "...", "tip": "..."}},
    {{"spanish": "...", "english": "...", "tip": "..."}},
    {{"spanish": "...", "english": "...", "tip": "..."}},
    {{"spanish": "...", "english": "...", "tip": "..."}},
    {{"spanish": "...", "english": "...", "tip": "..."}}
  ],
  "culture_note": "One interesting cultural insight related to this theme",
  "roadmap_hint": "One sentence on how this theme connects to the broader A1→B2 Spanish journey"
}}"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.6,
        )
        raw = response.choices[0].message.content.strip()
        # strip possible markdown fences
        import re
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"  [Spanish lesson error]: {e}")
        return {
            "theme": theme,
            "intro": "Today's lesson covers essential phrases.",
            "phrases": [
                {"spanish": "Hola, ¿cómo estás?", "english": "Hello, how are you?", "tip": "Most common greeting"},
                {"spanish": "Muy bien, gracias", "english": "Very well, thank you", "tip": "Standard polite reply"},
                {"spanish": "¿Cómo te llamas?", "english": "What is your name?", "tip": "Use 'te' informally"},
                {"spanish": "Me llamo Suhani", "english": "My name is Suhani", "tip": "Introduce yourself"},
                {"spanish": "Encantada", "english": "Nice to meet you (feminine)", "tip": "Use encantado if masculine"},
            ],
            "culture_note": "Spanish is spoken by 500M+ people worldwide.",
            "roadmap_hint": "Master these phrases to build your A1 foundation.",
        }

def build_html(date_str, summaries, market_data, spanish_lesson):
    # Market cards HTML
    market_cards = ""
    icons = {"Nifty 50": "📈", "S&P 500": "🗽", "Bitcoin": "₿", "Ethereum": "Ξ"}
    for name, data in market_data.items():
        price = data["price"]
        change = data["change"]
        color = "#7fd17f" if "+" in change else "#e07f7f" if "-" in change else "#ccc"
        icon = icons.get(name, "💹")
        market_cards += f"""
        <div class="market-card">
            <div class="market-icon">{icon}</div>
            <div class="market-name">{name}</div>
            <div class="market-price">{price}</div>
            <div class="market-change" style="color:{color}">{change}</div>
        </div>"""

    # Category sections HTML
    sections_html = ""
    category_icons = {
        "World Affairs": "🌍", "War & Conflicts": "⚔️", "India News": "🇮🇳",
        "Politics": "🏛️", "Technology": "💻", "AI & Data Science": "🤖",
        "Science": "🔬", "Business & Finance": "💼", "Trends & Pop Culture": "✨",
        "Entertainment": "🎬", "Wellness & Psychology": "🧠", "Lifestyle & Fashion": "👗",
        "Personal Growth & Career": "🚀", "General News": "📰",
    }
    for category, summary in summaries.items():
        icon = category_icons.get(category, "📌")
        sections_html += f"""
        <article class="news-section">
            <div class="section-header">
                <span class="section-icon">{icon}</span>
                <h2 class="section-title">{category}</h2>
            </div>
            <p class="section-body">{summary}</p>
        </article>"""

    # Spanish lesson HTML
    phrases_html = ""
    for i, p in enumerate(spanish_lesson.get("phrases", []), 1):
        phrases_html += f"""
        <div class="phrase-card">
            <div class="phrase-number">{i:02d}</div>
            <div class="phrase-content">
                <div class="phrase-spanish">{p['spanish']}</div>
                <div class="phrase-english">{p['english']}</div>
                <div class="phrase-tip">💡 {p['tip']}</div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Suhani's Daily Digest — {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0e0608;
    --bg2: #160b0e;
    --bg3: #1e0f13;
    --burgundy: #6b1a2e;
    --burgundy-light: #8b2340;
    --burgundy-glow: #b03055;
    --cream: #f0e8d8;
    --cream-dim: #c8bfad;
    --gold: #c9a84c;
    --gold-light: #e8c96a;
    --text: #e8e0d0;
    --text-dim: #998a7a;
    --border: rgba(107,26,46,0.35);
    --card-bg: rgba(22,11,14,0.95);
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Jost', sans-serif;
    font-weight: 300;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* Grain overlay */
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
  }}

  .wrapper {{ position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; padding: 0 2rem 4rem; }}

  /* ── MASTHEAD ── */
  .masthead {{
    border-bottom: 1px solid var(--border);
    padding: 3rem 0 2rem;
    text-align: center;
    position: relative;
  }}
  .masthead::after {{
    content: '';
    display: block;
    width: 120px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--burgundy-glow), transparent);
    margin: 1.5rem auto 0;
  }}
  .edition-label {{
    font-family: 'Jost', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1rem;
  }}
  .masthead h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 900;
    color: var(--cream);
    line-height: 0.95;
    letter-spacing: -0.02em;
  }}
  .masthead h1 span {{
    color: var(--burgundy-glow);
    font-style: italic;
  }}
  .masthead-sub {{
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    color: var(--text-dim);
    margin-top: 1rem;
    text-transform: uppercase;
  }}

  /* ── MARKET STRIP ── */
  .market-strip {{
    display: flex;
    gap: 1rem;
    margin: 2.5rem 0;
    flex-wrap: wrap;
  }}
  .market-card {{
    flex: 1;
    min-width: 160px;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    transition: border-color 0.2s;
  }}
  .market-card:hover {{ border-color: var(--burgundy-glow); }}
  .market-icon {{ font-size: 1.2rem; }}
  .market-name {{ font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-dim); }}
  .market-price {{ font-family: 'Playfair Display', serif; font-size: 1.3rem; color: var(--cream); font-weight: 700; }}
  .market-change {{ font-size: 0.8rem; font-weight: 500; }}

  /* ── SECTION GRID ── */
  .section-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
  }}

  /* ── NEWS SECTION ── */
  .news-section {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.8rem 2rem;
    transition: border-color 0.2s, transform 0.2s;
    position: relative;
    overflow: hidden;
  }}
  .news-section::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--burgundy), var(--burgundy-glow), var(--gold), transparent);
    opacity: 0;
    transition: opacity 0.3s;
  }}
  .news-section:hover {{ border-color: var(--burgundy-glow); transform: translateY(-2px); }}
  .news-section:hover::before {{ opacity: 1; }}

  .section-header {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1rem;
  }}
  .section-icon {{ font-size: 1.1rem; }}
  .section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--cream);
    letter-spacing: 0.01em;
  }}
  .section-body {{
    font-size: 0.88rem;
    line-height: 1.75;
    color: var(--cream-dim);
    font-weight: 300;
  }}

  /* ── SPANISH SECTION ── */
  .spanish-section {{
    background: linear-gradient(135deg, var(--bg3), rgba(107,26,46,0.15));
    border: 1px solid var(--burgundy);
    border-radius: 8px;
    padding: 2.5rem;
    margin-top: 2.5rem;
  }}
  .spanish-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }}
  .spanish-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--cream);
  }}
  .spanish-theme-badge {{
    background: var(--burgundy);
    color: var(--cream);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
  }}
  .spanish-intro {{
    font-size: 0.88rem;
    color: var(--cream-dim);
    margin-bottom: 1.5rem;
    line-height: 1.7;
  }}
  .phrases-grid {{
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }}
  .phrase-card {{
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    background: rgba(0,0,0,0.2);
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    border-left: 2px solid var(--burgundy-glow);
  }}
  .phrase-number {{
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: var(--burgundy-glow);
    font-weight: 700;
    min-width: 28px;
    line-height: 1.4;
  }}
  .phrase-spanish {{
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-style: italic;
    color: var(--gold-light);
    font-weight: 400;
  }}
  .phrase-english {{
    font-size: 0.82rem;
    color: var(--text-dim);
    margin-top: 0.15rem;
  }}
  .phrase-tip {{
    font-size: 0.75rem;
    color: var(--cream-dim);
    margin-top: 0.3rem;
    opacity: 0.8;
  }}
  .spanish-footer {{
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }}
  .spanish-note {{
    font-size: 0.82rem;
    color: var(--text-dim);
    line-height: 1.6;
  }}
  .spanish-note strong {{ color: var(--gold); font-weight: 500; }}

  /* ── FOOTER ── */
  .digest-footer {{
    text-align: center;
    padding: 2.5rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
    font-size: 0.75rem;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}

  /* ── SECTION HEADING ── */
  .block-heading {{
    font-family: 'Playfair Display', serif;
    font-size: 0.65rem;
    font-weight: 400;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--gold);
    margin: 3rem 0 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }}
  .block-heading::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }}

  /* Fade in */
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .masthead {{ animation: fadeUp 0.6s ease both; }}
  .market-strip {{ animation: fadeUp 0.6s 0.15s ease both; }}
  .news-section {{ animation: fadeUp 0.5s ease both; }}
  .spanish-section {{ animation: fadeUp 0.6s ease both; }}
</style>
</head>
<body>
<div class="wrapper">

  <header class="masthead">
    <div class="edition-label">Morning Edition · {date_str}</div>
    <h1>Suhani's <span>Daily</span> Digest</h1>
    <p class="masthead-sub">Curated · Summarised · Yours</p>
  </header>

  <div class="block-heading">Markets</div>
  <div class="market-strip">{market_cards}</div>

  <div class="block-heading">Today's Briefing</div>
  <div class="section-grid">{sections_html}</div>

  {build_spanish_html(spanish_lesson, phrases_html)}

  <footer class="digest-footer">
    Generated {date_str} · Powered by Groq llama-3.3-70b-versatile · Built for Suhani Khanna
  </footer>

</div>
</body>
</html>"""
    return html

def build_spanish_html(lesson, phrases_html):
    return f"""
  <section class="spanish-section">
    <div class="spanish-header">
      <div class="spanish-title">🇪🇸 Hoy en Español</div>
      <div class="spanish-theme-badge">{lesson.get('theme', 'Daily Spanish')}</div>
    </div>
    <p class="spanish-intro">{lesson.get('intro', '')}</p>
    <div class="phrases-grid">{phrases_html}</div>
    <div class="spanish-footer">
      <div class="spanish-note"><strong>Nota Cultural</strong><br>{lesson.get('culture_note', '')}</div>
      <div class="spanish-note"><strong>Tu Roadmap</strong><br>{lesson.get('roadmap_hint', '')}</div>
    </div>
  </section>"""

def send_email_digest(summaries, market_data, date_str):
    subject = f"☕ Suhani's Morning Digest — {date_str}"

    market_lines = "\n".join([
        f"  {name}: {d['price']} {d['change']}" for name, d in market_data.items()
    ])

    # Pick 4 key sections for the email
    key_sections = ["World Affairs", "India News", "Technology", "Personal Growth & Career"]
    digest_lines = ""
    for cat in key_sections:
        if cat in summaries:
            # Truncate to ~150 chars for email
            blurb = summaries[cat][:180] + "…" if len(summaries[cat]) > 180 else summaries[cat]
            digest_lines += f"\n\n{'─'*40}\n{cat.upper()}\n{blurb}"

    body = f"""Good morning, Suhani! ☀️

Here's your condensed morning briefing for {date_str}.

📊 MARKETS
{market_lines}
{digest_lines}

── 
Open your full HTML digest for all categories + Spanish lesson.
Generated by your Daily Digest script.
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print("  ✅ Email digest sent successfully.")
    except Exception as e:
        print(f"  ❌ Email failed: {e}")
        print("     Check your Gmail App Password in config.py")

def main():
    print(f"\n{'═'*55}")
    print(f"  ✨ Suhani's Daily Digest — {datetime.now().strftime('%A, %d %B %Y')}")
    print(f"{'═'*55}\n")

    client = Groq(api_key=GROQ_API_KEY)
    date_str = datetime.now().strftime("%A, %d %B %Y")

    # 1. Fetch market data
    print("📊 Fetching market data...")
    market_data = fetch_market_data()
    print(f"   Nifty: {market_data.get('Nifty 50', {}).get('price')} | BTC: {market_data.get('Bitcoin', {}).get('price')}")

    # 2. Fetch & summarize RSS categories
    summaries = {}
    for category, feeds in RSS_FEEDS.items():
        print(f"📰 [{category}] fetching headlines...")
        headlines = fetch_rss_headlines(feeds)
        print(f"   → {len(headlines)} headlines. Summarizing with Groq...")
        tone = TONE_INSTRUCTIONS.get(category, "Clear and informative.")
        summaries[category] = summarize_with_groq(client, category, headlines, tone)

    # 3. Spanish lesson
    theme = get_spanish_theme()
    print(f"\n🇪🇸 Generating Spanish lesson: {theme}...")
    spanish_lesson = generate_spanish_lesson(client, theme)

    # 4. Build HTML
    print("\n🎨 Building HTML dashboard...")
    html = build_html(date_str, summaries, market_data, spanish_lesson)
    output_path = Path(__file__).parent / "dashboard.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"   Saved: {output_path}")

    # 5. Send email
    print("\n📧 Sending email digest...")
    send_email_digest(summaries, market_data, date_str)

    # 6. Open browser
    print("\n🌐 Opening dashboard in browser...")
    webbrowser.open(f"file://{output_path.resolve()}")

    print(f"\n{'═'*55}")
    print("  ✅ Digest complete! Have a great day, Suhani.")
    print(f"{'═'*55}\n")

if __name__ == "__main__":
    main()
