<div align="center">

<img src="https://i.ibb.co/B56nZRw3/file-4027.jpg" alt="Bumpify Ads Bot" width="120" style="border-radius:16px"/>

<h1>🚀 Bumpify Ads Bot</h1>

<p><strong>Professional Telegram group ad broadcasting automation</strong><br>
Multi-account · All media types · AES-256 encrypted sessions · Real-time logs</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat-square&logo=mongodb&logoColor=white"/>
  <img src="https://img.shields.io/badge/Telegram-Bot%20API%209.4-0088CC?style=flat-square&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pyrogram-MTProto-2CA5E0?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-black?style=flat-square"/>
</p>

<p>
  <a href="https://t.me/pythontodayz">
    <img src="https://img.shields.io/badge/Telegram-Join%20Channel-0088CC?style=for-the-badge&logo=telegram&logoColor=white"/>
  </a>
  &nbsp;
  <a href="https://github.com/pooraddyy/bumpify-ads-bot">
    <img src="https://img.shields.io/badge/GitHub-Star%20Repo-black?style=for-the-badge&logo=github"/>
  </a>
</p>

> **⚠️ Beta:** This project is in active development. Open an [Issue](https://github.com/pooraddyy/bumpify-ads-bot/issues) for bugs, or fork and submit a pull request!

</div>

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🔁 | **Multi-Account** | Unlimited Telegram accounts, all handled concurrently |
| 📸 | **All Media Types** | Text, photo, video, document, audio, sticker, voice, video note |
| ✍️ | **Formatting Preserved** | Bold, italic, `code`, blockquote, strikethrough — fully kept |
| 📡 | **Two Send Modes** | Direct (stored content) or Forward (from Saved Messages) |
| 📊 | **Real-Time Logs** | Per-group logs: name, @username, link, ID, success/fail counts |
| 🤖 | **Auto-Reply** | Custom message auto-sent on incoming DMs to your accounts |
| 🔐 | **AES-256 Encryption** | Fernet + PBKDF2 — sessions never stored in plaintext |
| 🌐 | **Web Panel** | Telegram WebApp with 250+ country codes for account login |
| ⏱️ | **Custom Interval** | Presets (5 min → 2 hrs) or any custom seconds value |
| 🎨 | **Colored Buttons** | Bot API 9.4 native colored inline buttons |
| 🌊 | **Flood Protection** | Automatic FloodWait handling with smart retries |
| 🔒 | **Private Mode** | Restrict bot access to owner only |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Main bot token from [@BotFather](https://t.me/botfather) |
| `LOGGER_BOT_TOKEN` | ✅ | Logger bot token from [@BotFather](https://t.me/botfather) |
| `LOGGER_BOT_USERNAME` | ⬜ | Logger bot @username (without @) |
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `MONGODB_URL` | ✅ | MongoDB Atlas connection string |
| `ENCRYPTION_KEY` | ✅ | Min 32-char random secret key |
| `WEB_APP_URL` | ⬜ | Public HTTPS URL for the WebApp panel button |
| `WEB_PORT` | ⬜ | Web panel port (default: `3000`) |
| `LAST_NAME_SUFFIX` | ⬜ | Appended to account last names (default: `-Bumpify`) |
| `BIO_TEXT` | ⬜ | Bio set on account after login |
| `AUTO_REPLY_TEXT` | ⬜ | Default auto-reply message text |
| `PRIVATE_MODE` | ⬜ | Set `true` to restrict bot to owner only |
| `OWNER_ID` | ⬜ | Your Telegram user ID (required with `PRIVATE_MODE=true`) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (Atlas free tier works great)
- Two Telegram bot tokens from [@BotFather](https://t.me/botfather)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

### 1️⃣ Clone & enter directory

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure environment

```bash
cp .env.example .env
nano .env
```

### 4️⃣ Run

```bash
python main.py
```

---

## 🖥️ VPS Deployment (Ubuntu / Debian)

### Step 1 — Connect & prepare system

```bash
ssh root@your-server-ip
apt update && apt upgrade -y
apt install python3.11 python3-pip git -y
```

### Step 2 — Clone & install

```bash
git clone https://github.com/pooraddyy/bumpify-ads-bot.git
cd bumpify-ads-bot
pip install -r requirements.txt
```

### Step 3 — Configure environment

```bash
cp .env.example .env
nano .env
```

Fill in all required values, save with `Ctrl+X → Y → Enter`.

### Step 4 — Run with systemd (auto-restart on crash/reboot)

Create the service file:

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

Enable and start:

```bash
systemctl daemon-reload
systemctl enable bumpify
systemctl start bumpify
```

### Step 5 — Manage the service

```bash
systemctl status bumpify       # check running status
journalctl -u bumpify -f       # live logs
systemctl restart bumpify      # restart after changes
systemctl stop bumpify         # stop
```

### Step 6 — Update to latest version

```bash
cd /root/bumpify-ads-bot
git pull
systemctl restart bumpify
```

### Optional — HTTPS with Nginx (required for WebApp panel)

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

Then set `WEB_APP_URL=https://your-domain.com/panel` in `.env` and restart.

---

## ☁️ Cloud Platforms

### Railway

1. Fork this repo on GitHub
2. Connect to [Railway](https://railway.app) and select the forked repo
3. Set all environment variables in the Railway dashboard
4. Start command: `python main.py`

### Render

1. Fork this repo on GitHub
2. Create a new **Background Worker** on [Render](https://render.com)
3. Start command: `python main.py`
4. Set all environment variables in the Render dashboard

---

## 🔒 Security Notes

- Sessions are encrypted with **Fernet (AES-256 CBC + HMAC-SHA256)** before storing in MongoDB
- `ENCRYPTION_KEY` is processed through PBKDF2 — never stored raw
- Change `ENCRYPTION_KEY` before going to production and keep it private
- Never share your `.env` file or MongoDB connection string

---

## 🛠️ Contributing

```
Fork → Clone → Create branch → Make changes → Open Pull Request
```

**Ideas for contributions:**
- Better rate limiting and flood strategies
- Multi-language bot interface support
- Scheduled broadcasting (cron-style)
- Group blacklist / whitelist per account
- Per-account message customization

---

## 📢 Support & Community

<div align="center">

Join the Telegram channel for updates and announcements:

[![Telegram](https://img.shields.io/badge/Telegram-Join%20Channel-0088CC?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/pythontodayz)

If this project helped you, a ⭐ goes a long way:

[![GitHub](https://img.shields.io/badge/GitHub-Star%20Repo-black?style=for-the-badge&logo=github)](https://github.com/pooraddyy/bumpify-ads-bot)

</div>

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. Attribution appreciated but not required.
