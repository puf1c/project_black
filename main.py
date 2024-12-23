import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import asyncio
from weather_analyze import get_location_key_by_name, get_weather_parameters, get_weather_forecast

# ОБЯЗАТЕЛЬНО ЗАПОЛНИТЬ
TELEGRAM_BOT_TOKEN = "ваш телеграм токен"
ACCUWEATHER_API_KEY = "ваш ключ от accuweather"

# конфигурация бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# глобальные переменные для сохранения маршрута пользователя
user_routes = {}
user_intervals = {}

TIMEOUT = 10  # Тайм-аут в секундах для асинхронных вызовов

# обработка команды \start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я weather bot.\n\n"
        "Я помогу вам узнать погоду на маршруте на заданный промежуток времени. \n"
        "Команды: \n"
        "/weather - Узнать прогноз погоды для маршрута\n"
        "/help - Список команд\n"
    )

# обработка команды \help
@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(
        "Команды:\n"
        "/start - Начать работу с ботом\n"
        "/weather - Узнать прогноз погоды для маршрута\n"
        "/help - Список команд"
    )

# обработка команды \weather и получение временного интервала
@dp.message(Command('weather'))
async def weather_start(message: types.Message):
    user_routes[message.chat.id] = []
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="3 дня", callback_data="interval_3")
    keyboard.button(text="5 дней", callback_data="interval_5")
    keyboard.adjust(1)
    await message.reply("Выберите временной интервал прогноза погоды:", reply_markup=keyboard.as_markup())

# обработка временного интервала
@dp.callback_query(lambda c: c.data.startswith("interval_"))
async def process_time_interval(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    interval = int(callback_query.data.split("_")[1])
    user_intervals[user_id] = interval
    await bot.send_message(user_id, f"Вы выбрали прогноз на {interval} дней.")
    await bot.send_message(user_id, "Введите начальную точку маршрута (город):")

# принимает сообщение с городом
@dp.message()
async def process_city(message: types.Message):
    user_id = message.chat.id
    if user_id not in user_intervals:
        await message.reply("Сначала выберите временной интервал, используя команду /weather.")
        return

    if user_id not in user_routes:
        user_routes[user_id] = []

    user_routes[user_id].append(message.text)

    if len(user_routes[user_id]) == 1:
        await message.reply("Введите конечную точку маршрута (город):")
    else:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Добавить остановку", callback_data="add_stop")
        keyboard.button(text="Подтвердить маршрут", callback_data="confirm_route")
        keyboard.adjust(1)
        await message.reply("Хотите добавить остановку или подтвердить маршрут?", reply_markup=keyboard.as_markup())

# обработка добавления остановки или окончания маршрута
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
            interval = user_intervals.get(user_id, 3)  # Используем сохранённый интервал
            await bot.send_message(user_id, f"Ваш маршрут: {', '.join(route)}")
            await send_weather_forecast(user_id, route, interval)

# запрос прогноза погоды
async def send_weather_forecast(user_id, route, interval):
    try:
        forecast_results = []
        for city in route:
            try:
                location_key = await asyncio.wait_for(
                    get_location_key_by_name(city, ACCUWEATHER_API_KEY),
                    timeout=TIMEOUT
                )
                if not location_key:
                    forecast_results.append(f"{city}: Не удалось найти ключ локации.")
                    continue

                forecast = await asyncio.wait_for(
                    get_weather_forecast(api_key=ACCUWEATHER_API_KEY, location_key=location_key, days=5),
                    timeout=TIMEOUT
                )
                if forecast:
                    for day in forecast[:interval]:
                        forecast_results.append(
                            f"{city}:\n"
                            f"Дата: {day['date'][:10]}\n"
                            f"Максимальная температура: {day['max_temperature']}°C\n"
                            f"Минимальная температура: {day['min_temperature']}°C\n"
                            f"Скорость ветра: {day['wind_speed']} м/с\n"
                            f"Вероятность дождя: {day['precipitation_sum']}%\n"
                        )
                else:
                    forecast_results.append(f"{city}: Прогноз погоды недоступен.")
            except asyncio.TimeoutError:
                forecast_results.append(f"{city}: Время ожидания ответа истекло.")

        await bot.send_message(user_id, "\n\n".join(forecast_results))
    except Exception as e:
        await bot.send_message(user_id, f"Ошибка при получении прогноза: {str(e)}")

# запуск бота
if __name__ == "__main__":
    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())