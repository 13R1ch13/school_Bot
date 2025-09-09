
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
TZ = os.getenv("TZ", "Europe/Kyiv")
ORDER_LINK = os.getenv("ORDER_LINK", "")

PRICES = {
    "комплекс": 300,
    "сніданок_обід": 250,
    "обід_полуденок": 200,
    "обід": 150,
}
