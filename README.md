<div align="center">

<img src="https://i.ibb.co/B56nZRw3/file-4027.jpg" alt="Bumpify Ads Bot" width="120" style="border-radius:16px"/>

<h1>🚀 Bumpify Ads Bot</h1>

<p><strong>Professional Telegram group ad broadcasting automation</strong><br>Multi-account · All media types · AES-256 encrypted sessions · Real-time analytics</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/Telegram-Bot%20API%20v20-0088CC?style=flat-square&logo=telegram&logoColor=white" alt="Telegram"/>
  <img src="https://img.shields.io/badge/Pyrogram-MTProto-2CA5E0?style=flat-square" alt="Pyrogram"/>
  <img src="https://img.shields.io/badge/License-MIT-black?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/Status-Beta-orange?style=flat-square" alt="Beta"/>
</p>

<p>
  <a href="https://t.me/pythontodayz">
    <img src="https://img.shields.io/badge/📢%20Join%20Channel-@pythontodayz-0088CC?style=for-the-badge&logo=telegram&logoColor=white" alt="Join Channel"/>
  </a>
  &nbsp;
  <a href="https://github.com/pooraddyy/bumpify-ads-bot">
    <img src="https://img.shields.io/badge/⭐%20Star%20on-GitHub-black?style=for-the-badge&logo=github" alt="Star on GitHub"/>
  </a>
</p>

> **⚠️ Beta Notice:** This project is in active development. Some features may be incomplete or have bugs. If you encounter issues, please open an [Issue](https://github.com/pooraddyy/bumpify-ads-bot/issues). We welcome contributions — feel free to **fork**, improve, and submit a pull request!

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔁 **Multi-account** | Unlimited Telegram accounts, all handled concurrently |
| 📸 **All media types** | Text, photo, video, document, audio, animation, sticker, voice, video note |
| ✍️ **Formatting preserved** | Bold, italic, `code`, blockquote, strikethrough — fully preserved |
| 📡 **Two send modes** | Direct (stored content) or Forward (from Saved Messages) |
| 📊 **Real-time analytics** | Per-group reports: name, @username, link, ID, success/fail |
| 🤖 **Auto-reply** | Custom message auto-sent on incoming DMs |
| ⏸️ **Account toggle** | Activate/deactivate accounts without removing them |
| 🔐 **AES-256 encryption** | Fernet + PBKDF2, sessions never stored in plaintext |
| 🌐 **Web panel** | Telegram WebApp with 250+ country codes |
| ⏱️ **Custom interval** | Presets (5 min → 2 hrs) or any custom seconds |
| 🔄 **Non-blocking** | Multiple users and accounts handled fully concurrently |
| 🌊 **Flood protection** | Automatic FloodWait handling with smart retries |

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | ✅ | — | Main bot token from @BotFather |
| `TRACKING_BOT_TOKEN` | ✅ | — | Tracking bot token from @BotFather |
| `TRACKING_BOT_USERNAME` | ⬜ | — | Tracking bot @username |
| `API_ID` | ✅ | — | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | — | From [my.telegram.org](https://my.telegram.org) |
| `MONGODB_URL` | ✅ | — | MongoDB connection string |
| `ENCRYPTION_KEY` | ✅ | — | Min 32 chars random secret |
| `WEB_APP_URL` | ⬜ | — | Public HTTPS URL for WebApp button |
| `WEB_PORT` | ⬜ | `3000` | Web panel port |
| `LAST_NAME_SUFFIX` | ⬜ | `-Bumpify` | Appended to account last names |
| `BIO_TEXT` | ⬜ | `Managed by Bumpify...` | Bio set after account login |
| `AUTO_REPLY_TEXT` | ⬜ | `I'm offline...` | Default auto-reply message |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (Atlas free tier works perfectly)
- Two Telegram bot tokens from [@BotFather](https://t.me/botfather)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

### 1️⃣ Clone

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot/bumpify-bot
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure

```bash
cp .env.example .env
nano .env    # fill in all values
```

### 4️⃣ Run

```bash
python main.py
```

---

## 🖥️ VPS Deployment (Ubuntu / Debian)

Complete guide for deploying on any Linux VPS (DigitalOcean, Hetzner, Contabo, AWS EC2, etc.)

### Step 1 — Connect to your VPS

```bash
ssh root@your-server-ip
```

### Step 2 — Update system and install Python

```bash
apt update && apt upgrade -y
apt install python3.11 python3.11-pip python3.11-venv git -y
```

### Step 3 — Clone the repo

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot/bumpify-bot
```

### Step 4 — Create virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5 — Set up environment

```bash
cp .env.example .env
nano .env
```

Fill in all required values, then save (`Ctrl+X → Y → Enter`).

### Step 6 — Test run

```bash
python main.py
```

Press `Ctrl+C` after confirming it starts without errors.

### Step 7 — Run with systemd (auto-restart on crash/reboot)

Create the service file:

```bash
nano /etc/systemd/system/bumpify.service
```

Paste this (replace `/root/bumpify-ads-bot` with your actual path):

```ini
[Unit]
Description=Bumpify Ads Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/bumpify-ads-bot/bumpify-bot
ExecStart=/root/bumpify-ads-bot/bumpify-bot/venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
systemctl daemon-reload
systemctl enable bumpify
systemctl start bumpify
```

### Step 8 — Check status and logs

```bash
# Check if running
systemctl status bumpify

# Live logs
journalctl -u bumpify -f

# Restart after changes
systemctl restart bumpify

# Stop
systemctl stop bumpify
```

### Step 9 — Update to latest version

```bash
cd /root/bumpify-ads-bot
git pull
systemctl restart bumpify
```

### Optional — HTTPS with Nginx (needed for WebApp button)

```bash
apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx config:

```bash
nano /etc/nginx/sites-available/bumpify
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /panel {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:3000;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:3000;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/bumpify /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Get SSL certificate
certbot --nginx -d your-domain.com
```

Then set `WEB_APP_URL=https://your-domain.com/panel` in `.env` and restart.

---

## ☁️ Cloud Platforms

### Railway

1. Fork this repo
2. Connect to [Railway](https://railway.app)
3. Set all env vars in Railway dashboard
4. Start command: `cd bumpify-bot && python main.py`

### Render

1. Fork this repo
2. Create new Web Service on [Render](https://render.com)
3. Root directory: `bumpify-bot`
4. Start command: `python main.py`
5. Set all env vars

---

## 🔒 Security Notes

- Sessions are encrypted with **Fernet (AES-256 CBC + HMAC-SHA256)** before storing in MongoDB
- The `ENCRYPTION_KEY` is never stored raw — it's processed through PBKDF2
- Change `ENCRYPTION_KEY` before production and keep it secret
- Never share your `.env` file or MongoDB credentials

---

## 🛠️ Contributing

This is a **beta project** — bugs are expected and many features can be improved.

```
Fork → Clone → Create branch → Make changes → Open Pull Request
```

Ideas for contributions:
- Better rate limiting strategies
- Dashboard UI improvements
- Multi-language support
- Scheduled broadcasting (cron-style)
- Group blacklist/whitelist
- Per-account message customization
- Web panel account management improvements

---

## 📢 Support & Community

<div align="center">

Join the Telegram channel for updates, tips, and announcements:

[![Join Channel](https://img.shields.io/badge/📢%20@pythontodayz-Join%20Channel-0088CC?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/pythontodayz)

If this project saved you time, a ⭐ goes a long way:

[![Star on GitHub](https://img.shields.io/badge/⭐%20Star%20on-GitHub-black?style=for-the-badge&logo=github)](https://github.com/pooraddyy/bumpify-ads-bot)

</div>

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. Attribution appreciated but not required.
