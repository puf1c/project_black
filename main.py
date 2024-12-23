import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ОБЯЗАТЕЛЬНО ЗАПОЛНИТЬ
TELEGRAM_BOT_TOKEN = "8035942674:AAHj-Q8ngroe-eTTrIZ0Ew4bSS5xfYbfCaw"
ACCUWEATHER_API_KEY = "1RpoYQwn5aPvAfnRgHO5HvsEUIwhJK4p"
YANDEX_API_KEY = "ваш_ключ_Яндекс_геокодера"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

