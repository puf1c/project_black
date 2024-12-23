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

user_routes = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я weather bot.\n\n"
        "Я помогу тебе узнать погоду на маршруте на заданный промежуток времени. \n"
        "Команды: \n"
        "/weather - Узнать прогноз погоды для маршрута\n"
        "/help - Список команд"
    )

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply(
        "Команды:\n"
        "/start - Начать работу с ботом\n"
        "/weather - Узнать прогноз погоды для маршрута\n"
        "/help - Список команд"
    )

