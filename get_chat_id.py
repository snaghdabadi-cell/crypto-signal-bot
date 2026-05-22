import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"
response = requests.get(url, timeout=30)

print(response.json())