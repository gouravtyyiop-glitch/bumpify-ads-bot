<div align="center">

<h1>Bumpify Ads Bot</h1>

<p>Professional Telegram group ad broadcasting automation with multi-account support, real-time analytics, AES-256 encrypted sessions, and a Telegram WebApp panel.</p>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API%20v20-0088CC?style=flat-square&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-MTProto-2CA5E0?style=flat-square)](https://pyrogram.org)
[![License](https://img.shields.io/badge/License-MIT-black?style=flat-square)](LICENSE)

[Join Channel](https://t.me/pythontodayz) · [Report Bug](https://github.com/pooraddyy/bumpify-ads-bot/issues) · [Give a Star ⭐](https://github.com/pooraddyy/bumpify-ads-bot)

</div>

---

## Features

- **Multi-account broadcasting** — unlimited Telegram accounts, all handled concurrently
- **All media types** — text, photo, video, document, audio, animation, sticker, voice, video note
- **Full formatting preserved** — bold, italic, code, blockquote, strikethrough, underline
- **Direct & Forward mode** — send stored content or forward from Saved Messages
- **Real-time analytics** — per-group tracking (name, username, link, ID) sent to your tracking bot
- **Auto-reply** — custom message auto-sent on incoming private messages
- **Account activate/deactivate** — pause individual accounts without removing them
- **AES-256 encrypted sessions** — Fernet + PBKDF2, never stored in plaintext
- **Web panel** — Telegram WebApp with full account management and 250+ country codes
- **Adjustable interval** — presets (5 min → 2 hrs) or custom seconds
- **Session persistence** — sessions survive restarts and never expire unless revoked
- **Concurrent requests** — multiple users and multiple accounts handled simultaneously
- **Flood protection** — automatic FloodWait handling with retries
- **Two-bot system** — main bot + separate tracking bot for clean analytics

---

## Architecture

```
bumpify-bot/
├── main.py                    — entry point, starts all three services
├── bot/
│   ├── config.py              — env var loading
│   ├── handlers/
│   │   ├── start.py           — /start command
│   │   ├── dashboard.py       — main control panel
│   │   ├── ads.py             — ad message set / start / stop
│   │   ├── accounts.py        — my accounts / delete
│   │   ├── auto_reply.py      — auto-reply toggle and custom text
│   │   ├── interval.py        — broadcast interval settings
│   │   ├── faq.py             — FAQ and how-to
│   │   └── callbacks.py       — inline button router
│   └── utils/
│       ├── db.py              — MongoDB CRUD (motor async)
│       ├── broadcaster.py     — concurrent async broadcast engine
│       ├── session_manager.py — Pyrogram login / session export
│       ├── auto_reply_manager.py — persistent auto-reply clients
│       ├── encryption.py      — AES-256 Fernet encrypt/decrypt
│       └── helpers.py         — safe_edit utility
├── tracking_bot/
│   └── handlers.py            — analytics tracking bot
└── web/
    ├── app.py                 — aiohttp web server + REST API
    ├── templates/index.html   — Telegram WebApp UI
    └── static/
        ├── style.css          — white/black professional theme
        └── app.js             — all logic + 250+ country codes
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (Atlas free tier works)
- Two Telegram bot tokens (from [@BotFather](https://t.me/botfather))
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

### 1. Clone the repo

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot/bumpify-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

```env
BOT_TOKEN=your_main_bot_token
TRACKING_BOT_TOKEN=your_tracking_bot_token
TRACKING_BOT_USERNAME=YourTrackingBot
API_ID=your_api_id
API_HASH=your_api_hash
MONGODB_URL=mongodb+srv://...
ENCRYPTION_KEY=your_random_secret_min_32_chars
WEB_APP_URL=https://your-domain.com/panel
WEB_PORT=3000
```

### 4. Run

```bash
python main.py
```

All three services start automatically:
- Main bot (handles user interactions)
- Tracking bot (delivers analytics)
- Web panel on port 3000

---

## Configuration

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Main bot token from @BotFather |
| `TRACKING_BOT_TOKEN` | Yes | Tracking bot token from @BotFather |
| `TRACKING_BOT_USERNAME` | No | Tracking bot @username (shown in start message) |
| `API_ID` | Yes | From my.telegram.org |
| `API_HASH` | Yes | From my.telegram.org |
| `MONGODB_URL` | Yes | MongoDB connection string |
| `ENCRYPTION_KEY` | Yes | Min 32 chars random secret for session encryption |
| `WEB_APP_URL` | No | Public HTTPS URL for Telegram WebApp button |
| `WEB_PORT` | No | Web panel port (default: 3000) |
| `LAST_NAME_SUFFIX` | No | Appended to account last names (default: -Bumpify) |
| `BIO_TEXT` | No | Bio set after account login |
| `AUTO_REPLY_TEXT` | No | Default auto-reply message text |

---

## Deployment

### Railway / Render

1. Push to GitHub
2. Connect repo to Railway or Render
3. Set all environment variables in the dashboard
4. Set start command: `cd bumpify-bot && python main.py`

### VPS (Ubuntu)

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot/bumpify-bot
pip install -r requirements.txt
cp .env.example .env
# fill in .env
python main.py
```

With `systemd` for auto-restart:

```ini
[Unit]
Description=Bumpify Ads Bot
After=network.target

[Service]
WorkingDirectory=/path/to/bumpify-ads-bot/bumpify-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Docker

```bash
docker build -t bumpify-bot .
docker run -d --env-file .env bumpify-bot
```

---

## How It Works

1. User adds Telegram accounts via the web panel (phone + OTP)
2. Sessions are exported as Pyrogram session strings and encrypted with AES-256 before storage
3. User sets an ad message (any media type — all formatting is preserved)
4. Bot broadcasts to every group of every active account concurrently
5. After each cycle, the tracking bot sends a detailed report:
   - Per-account summary
   - Each group: name, @username, direct link, Telegram ID
   - Success/failed counts
   - Next cycle countdown

---

## Security

- Sessions encrypted with Fernet (AES-256 in CBC mode) before MongoDB storage
- ENCRYPTION_KEY derived with PBKDF2 — never stored raw
- No session data ever logged or transmitted in plaintext
- Change ENCRYPTION_KEY before production deployment

---

## Support

<div align="center">

**Join the Telegram channel for updates, tips, and support:**

[![Join Channel](https://img.shields.io/badge/Telegram-Join%20@pythontodayz-0088CC?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/pythontodayz)

**If this project helped you, a star means a lot:**

[![Star on GitHub](https://img.shields.io/badge/GitHub-Give%20a%20Star%20%E2%AD%90-black?style=for-the-badge&logo=github)](https://github.com/pooraddyy/bumpify-ads-bot)

</div>

---

## License

MIT — use freely, attribution appreciated.
