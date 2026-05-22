## Bumpify Ads Bot — Setup Guide

### Step 1: Get Telegram API credentials
- Go to https://my.telegram.org/apps
- Create an app and note your `API_ID` and `API_HASH`

### Step 2: Create two bots on @BotFather
1. Main bot → copy token to `BOT_TOKEN`
2. Tracking bot → copy token to `TRACKING_BOT_TOKEN`, username to `TRACKING_BOT_USERNAME`

### Step 3: Edit .env
Copy `.env.example` to `.env` and fill in all values.
MongoDB URL is already set. Just update the bot tokens and API credentials.

### Step 4: Run locally
```
pip install -r requirements.txt
python main.py
```

### Step 5: Deploy to Railway (one click)
- Push this folder to GitHub
- Go to railway.app → New Project → Deploy from GitHub
- Set all env vars from your .env file

### Step 6: Deploy to Render
- Push to GitHub
- Go to render.com → New Web Service → connect repo
- Set env vars

### Step 7: Deploy to VPS
```
docker-compose up -d
```

### Web Panel URL
After deploying, your WEB_APP_URL will be:
`https://your-domain.com/panel`
Set this in your .env so the Add Account button works as a Telegram Web App.

### Bot Features
- /start — welcome screen with image
- Dashboard — all controls
- Add Account (web panel) — login via phone + OTP
- Set Ad Message — send any text/formatted message
- Start Ads — broadcasts to all groups (not channels)
- Stop Ads — stop immediately
- Toggle Mode — Direct or Forward
- Analytics — success/fail stats
- FAQ — usage guide
