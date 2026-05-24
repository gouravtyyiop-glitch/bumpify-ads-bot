<div align="center">

<img src="https://i.ibb.co/B56nZRw3/file-4027.jpg" width="100" style="border-radius:18px" alt="Bumpify"/>

<h1>Bumpify Ads Bot</h1>

<p>Professional Telegram group ad broadcasting automation.<br>
Multi-account &nbsp;·&nbsp; AES-256 encrypted sessions &nbsp;·&nbsp; Real-time logs &nbsp;·&nbsp; Web analytics panel</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pyrogram-MTProto-2CA5E0?style=flat-square&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat-square&logo=mongodb&logoColor=white"/>
  <img src="https://img.shields.io/badge/Bot_API-9.4-0088CC?style=flat-square&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-111827?style=flat-square"/>
</p>

<p>
  <a href="https://t.me/pythontodayz">
    <img src="https://img.shields.io/badge/Telegram-Channel-0088CC?style=for-the-badge&logo=telegram&logoColor=white"/>
  </a>
  &nbsp;
  <a href="https://github.com/pooraddyy/bumpify-ads-bot/stargazers">
    <img src="https://img.shields.io/github/stars/pooraddyy/bumpify-ads-bot?style=for-the-badge&color=f59e0b&logo=github&logoColor=white"/>
  </a>
</p>

</div>

<br>

---

## Features

<table>
<tr>
<td width="140"><img src="https://img.shields.io/badge/Multi--Account-6366f1?style=flat-square&logoColor=white"/></td>
<td>Unlimited Telegram accounts broadcasting concurrently with per-account isolation and session management</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Saved_Messages-10b981?style=flat-square&logoColor=white"/></td>
<td>Forwards directly from each account's Saved Messages — no re-upload, formatting preserved exactly</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/All_Media-f59e0b?style=flat-square&logoColor=white"/></td>
<td>Text, photo, video, document, audio, sticker, voice, video note — every Telegram media type supported</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Logger_Bot-0ea5e9?style=flat-square&logoColor=white"/></td>
<td>Per-group logs with name, @username, link, ID, success / fail count sent after every broadcast cycle</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Web_Panel-8b5cf6?style=flat-square&logoColor=white"/></td>
<td>Telegram WebApp for account login (250+ country codes) and a full analytics dashboard</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Analytics-ec4899?style=flat-square&logoColor=white"/></td>
<td>Total sent, success rate, per-account performance bars with progress indicators, recent activity feed</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Auto_Reply-14b8a6?style=flat-square&logoColor=white"/></td>
<td>Custom message auto-sent on incoming DMs to any connected account</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/AES--256-ef4444?style=flat-square&logoColor=white"/></td>
<td>Fernet + PBKDF2-HMAC-SHA256 — sessions never stored in plaintext in the database</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Flood_Protection-f97316?style=flat-square&logoColor=white"/></td>
<td>Automatic FloodWait handling with smart retries, concurrency semaphores, and per-group delays</td>
</tr>
<tr>
<td><img src="https://img.shields.io/badge/Private_Mode-64748b?style=flat-square&logoColor=white"/></td>
<td>Restrict bot to a comma-separated list of authorized owner IDs — all others are blocked on contact</td>
</tr>
</table>

---

## Environment Variables

| Variable | Required | Description |
|---|:---:|---|
| `BOT_TOKEN` | Yes | Main bot token from [@BotFather](https://t.me/botfather) |
| `LOGGER_BOT_TOKEN` | Yes | Logger bot token from [@BotFather](https://t.me/botfather) |
| `LOGGER_BOT_USERNAME` | No | Logger bot @username without the @ symbol |
| `API_ID` | Yes | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Yes | Telegram API hash from [my.telegram.org](https://my.telegram.org) |
| `MONGODB_URL` | Yes | MongoDB connection string (Atlas free tier works) |
| `ENCRYPTION_KEY` | Yes | Min 32-char secret key used for session encryption |
| `WEB_APP_URL` | No | Public HTTPS URL for the WebApp panel |
| `WEB_PORT` | No | Web server port — default `3000` |
| `OWNER_IDS` | No | Comma-separated Telegram user IDs e.g. `123456,789012` |
| `PRIVATE_MODE` | No | Set `true` to restrict all bot access to `OWNER_IDS` |
| `LAST_NAME_SUFFIX` | No | Appended to account last names — default `-Bumpify` |
| `BIO_TEXT` | No | Bio text applied to each account after login |
| `AUTO_REPLY_TEXT` | No | Default auto-reply message for incoming DMs |
| `START_IMAGE_URL` | No | Image shown in the bot start message |

---

## Quick Start

**Prerequisites** — Python 3.11+, MongoDB, two bot tokens from [@BotFather](https://t.me/botfather), API credentials from [my.telegram.org](https://my.telegram.org)

```bash
# Clone
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env

# Run
python main.py
```

---

## VPS Deployment

### 1 — Prepare server

```bash
ssh root@your-server-ip
apt update && apt upgrade -y
apt install python3.11 python3-pip git -y
```

### 2 — Install

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot
pip install -r requirements.txt
cp .env.example .env
nano .env
```

### 3 — systemd service

```bash
nano /etc/systemd/system/bumpify.service
```

```ini
[Unit]
Description=Bumpify Ads Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/bumpify-ads-bot
ExecStart=/usr/bin/python3.11 main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable bumpify
systemctl start bumpify
```

### 4 — Manage

```bash
systemctl status bumpify       # running status
journalctl -u bumpify -f       # live log stream
systemctl restart bumpify      # restart after changes
systemctl stop bumpify         # stop
```

### 5 — Update

```bash
cd /root/bumpify-ads-bot && git pull && systemctl restart bumpify
```

---

## HTTPS + Nginx

Required for the Telegram WebApp panel to function inside Telegram.

```bash
apt install nginx certbot python3-certbot-nginx -y
nano /etc/nginx/sites-available/bumpify
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /panel  { proxy_pass http://127.0.0.1:3000; proxy_set_header Host $host; }
    location /static { proxy_pass http://127.0.0.1:3000; }
    location /api    { proxy_pass http://127.0.0.1:3000; }
}
```

```bash
ln -s /etc/nginx/sites-available/bumpify /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
certbot --nginx -d your-domain.com
```

Set `WEB_APP_URL=https://your-domain.com/panel` in `.env` and restart.

---

## Cloud Platforms

**Railway** — Fork the repo, connect at [railway.app](https://railway.app), set env vars, start command: `python main.py`

**Render** — Fork the repo, create a Background Worker at [render.com](https://render.com), start command: `python main.py`, set env vars

---

## Project Structure

```
bumpify-ads-bot/
├── main.py                      Entry point — bot, web server, logger startup
├── bot/
│   ├── config.py                Environment variable loading
│   ├── handlers/
│   │   ├── start.py             /start command
│   │   ├── dashboard.py         Dashboard builder
│   │   ├── callbacks.py         Inline button router
│   │   ├── ads.py               Ad set, remove, start, stop
│   │   ├── accounts.py          Account list and analytics
│   │   ├── interval.py          Broadcast interval settings
│   │   ├── auto_reply.py        Auto-reply configuration
│   │   └── faq.py               FAQ and how-to
│   └── utils/
│       ├── broadcaster.py       Core broadcast engine (Pyrogram)
│       ├── db.py                MongoDB interface via Motor
│       ├── session_manager.py   Account login and session encryption
│       └── helpers.py           Shared utilities — safe_edit etc
├── logger_bot/
│   └── handlers.py              Logger bot /start and log dispatch
└── web/
    ├── app.py                   aiohttp REST API server
    ├── templates/index.html     Telegram WebApp UI
    └── static/                  CSS and JS for the web panel
```

---

## Security

Sessions are encrypted with **Fernet (AES-256 CBC + HMAC-SHA256)** before being stored in MongoDB.
The `ENCRYPTION_KEY` is processed through **PBKDF2-HMAC-SHA256** with a random salt — never used raw.

Keep `ENCRYPTION_KEY` and `MONGODB_URL` private. Never commit your `.env` file.

---

## Contributing

```
Fork  →  Clone  →  New branch  →  Changes  →  Pull request
```

Ideas welcome — scheduled broadcasts, per-account message customization, group whitelist/blacklist, multi-language support.

---

## Support

<div align="center">

<a href="https://t.me/pythontodayz">
  <img src="https://img.shields.io/badge/Telegram-Join_Channel-0088CC?style=for-the-badge&logo=telegram&logoColor=white"/>
</a>
&nbsp;
<a href="https://github.com/pooraddyy/bumpify-ads-bot/issues">
  <img src="https://img.shields.io/badge/GitHub-Open_Issue-111827?style=for-the-badge&logo=github&logoColor=white"/>
</a>

</div>

---

## License

MIT — see [LICENSE](LICENSE) for full text. Free to use, modify, and distribute.

---

<div align="center">
  <sub>Built with &nbsp;<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" height="16"/> &nbsp;<img src="https://img.shields.io/badge/Pyrogram-2CA5E0?style=flat-square&logo=telegram&logoColor=white" height="16"/> &nbsp;<img src="https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white" height="16"/> &nbsp;<img src="https://img.shields.io/badge/aiohttp-2C5282?style=flat-square" height="16"/></sub>
</div>
