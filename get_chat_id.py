import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"
response = requests.get(url)

print(response.json())