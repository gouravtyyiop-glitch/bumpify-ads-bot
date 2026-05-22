import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
TRACKING_BOT_TOKEN = os.environ["TRACKING_BOT_TOKEN"]
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
MONGODB_URL = os.environ["MONGODB_URL"]
ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]

LAST_NAME_SUFFIX = os.getenv("LAST_NAME_SUFFIX", "-Bumpify")
BIO_TEXT = os.getenv("BIO_TEXT", "Managed by Bumpify | Telegram Ad Automation")
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "")

_raw_caption = os.getenv("START_CAPTION", "")
if _raw_caption:
    START_CAPTION = _raw_caption.replace("\\n", "\n")
else:
    START_CAPTION = (
        "**\U0001f680 Welcome to Bumpify Ads Bot**\n\n"
        "The most powerful Telegram group advertising automation.\n\n"
        "\u2022 **Premium Ad Broadcasting**\n"
        "\u2022 **Smart Delays & Flood Protection**\n"
        "\u2022 **Multi-Account Support**\n"
        "\u2022 **Real-Time Analytics**"
    )

TRACKING_BOT_USERNAME = os.getenv("TRACKING_BOT_USERNAME", "")
WEB_APP_URL = os.getenv("WEB_APP_URL", "")
WEB_PORT = int(os.getenv("WEB_PORT", os.getenv("PORT", "3000")))

DATABASE_NAME = "bumpify"
