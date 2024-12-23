import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import asyncio
from weather_analyze import get_location_key_by_name, get_weather_parameters, get_weather_forecast

# ОБЯЗАТЕЛЬНО ЗАПОЛНИТЬ
TELEGRAM_BOT_TOKEN = "8035942674:AAHj-Q8ngroe-eTTrIZ0Ew4bSS5xfYbfCaw"
ACCUWEATHER_API_KEY = "1RpoYQwn5aPvAfnRgHO5HvsEUIwhJK4p"
YANDEX_API_KEY = "ваш_ключ_Яндекс_геокодера"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_routes = {}
user_intervals = {}

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я weather bot.\n\n"
        "Я помогу тебе узнать погоду на маршруте на заданный промежуток времени. \n"
        "Команды: \n"
        "/weather - Узнать прогноз погоды для маршрута\n"
        "/help - Список команд\n"
    )

@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(
        "Команды:\n"
        "/start - Начать работу с ботом\n"
        "/weather - Узнать прогноз погоды для маршрута\n"
        "/help - Список команд"
    )



@dp.message(Command('weather'))
async def weather_start(message: types.Message):
    user_routes[message.chat.id] = []
    await message.reply("Введите начальную точку маршрута (город):")

@dp.message()
async def process_city(message: types.Message):
    user_id = message.chat.id
    if user_id not in user_routes:
        await message.reply("Пожалуйста, введите /weather для начала работы.")
        return

    user_routes[user_id].append(message.text)

    if len(user_routes[user_id]) == 1:
        await message.reply("Введите конечную точку маршрута (город):")
    else:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Добавить остановку", callback_data="add_stop")
        keyboard.button(text="Подтвердить маршрут", callback_data="confirm_route")
        keyboard.adjust(1)  # Разместить кнопки в один столбец
        await message.reply("Хотите добавить остановку или подтвердить маршрут?", reply_markup=keyboard.as_markup())

@dp.callback_query(lambda c: c.data in ["add_stop", "confirm_route"])
async def process_route_actions(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id

    if callback_query.data == "add_stop":
        await bot.send_message(user_id, "Введите город для остановки:")
    elif callback_query.data == "confirm_route":
        route = user_routes.get(user_id, [])
        if len(route) < 2:
            await bot.send_message(user_id, "Маршрут должен содержать как минимум начальную и конечную точки.")
        else:
            await bot.send_message(user_id, f"Ваш маршрут: {', '.join(route)}")
            await send_weather_forecast(user_id, route, interval)

async def ask_time_interval(user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="3 дня", callback_data="interval_3")
    keyboard.button(text="5 дней", callback_data="interval_5")
    keyboard.adjust(1)
    await bot.send_message(user_id, "Выберите временной интервал прогноза погоды:", reply_markup=keyboard.as_markup())

@dp.callback_query(lambda c: c.data.startswith("interval_"))
async def process_time_interval(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    interval = int(callback_query.data.split("_")[1])
    user_intervals[user_id] = interval
    route = user_routes.get(user_id, [])
    await bot.send_message(user_id, f"Прогноз будет рассчитан на {interval} дней.")
    await send_weather_forecast(user_id, route, interval)

async def send_weather_forecast(user_id, route, interval):
    try:
        forecast_results = []
        for city in route:
            location_key = get_location_key_by_name(city, ACCUWEATHER_API_KEY)
            if not location_key:
                forecast_results.append(f"{city}: Не удалось найти ключ локации.")
                continue

            forecast = get_weather_forecast(api_key=ACCUWEATHER_API_KEY, location_key=location_key, days=interval)
            if forecast:
                for day in forecast:
                    forecast_results.append(
                        f"{city}:\n"
                        f"Дата: {day['date']}\n"
                        f"Температура: {day['temperature']}°C\n"
                        f"Скорость ветра: {day['wind_speed']} м/с\n"
                        f"Вероятность дождя: {day['rain_probability']}%\n"
                    )
            else:
                forecast_results.append(f"{city}: Прогноз погоды недоступен.")

        await bot.send_message(user_id, "\n\n".join(forecast_results))
    except Exception as e:
        await bot.send_message(user_id, f"Ошибка при получении прогноза: {str(e)}")


if __name__ == "__main__":
    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())

