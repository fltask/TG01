import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.client.default import DefaultBotProperties
import requests
import sys




# Загрузка токена из файла .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    return response.json()

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("🌤️ <b>Привет! Я бот погоды!</b>\n\n"
                        "Я могу показать тебе погоду в любом городе мира!\n\n"
                        "🌍 <b>Используйте:</b> /weather Город")

@dp.message(Command("weather"))
async def weather_command(message: Message):
    # Получаем аргументы команды
    args = message.text.split()
    
    if len(args) > 1:
        # Если указан город
        city = ' '.join(args[1:])  # Объединяем все слова после /weather
        await get_weather_info(message, city)
    else:
        # Если город не указан, используем Москву по умолчанию
        await get_weather_info(message, "Москва")

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer("🌤️ <b>Я бот погоды!</b>\n\n"
                        "К сожалению, я умею только показывать погоду в любом городе мира.\n\n"
                        "🌍 <b>Используйте:</b> /weather Город")

async def get_weather_info(message: Message, city: str):
    weather = get_weather(city)
    if weather.get('cod') == 200:
        temp = weather['main']['temp']
        description = weather['weather'][0]['description']
        humidity = weather['main']['humidity']
        wind = weather['wind']['speed']
        # Определяем эмодзи для погоды
        weather_emoji = {
            'ясно': '☀️',
            'облачно': '☁️',
            'пасмурно': '⛅',
            'дождь': '🌧️',
            'снег': '❄️',
            'туман': '🌫️',
            'гроза': '⛈️',
            'clear': '☀️',
            'clouds': '☁️',
            'rain': '🌧️',
            'snow': '❄️',
            'mist': '🌫️',
            'thunderstorm': '⛈️'
        }
        
        # Получаем эмодзи для текущей погоды
        emoji = weather_emoji.get(description.lower(), '🌤️')
        
        await message.answer(f"🌍 <b>Погода в городе {city.capitalize()}</b>\n\n"
           f"{emoji} <b>{description.capitalize()}</b>\n"
           f"🌡️ <b>Температура:</b> {temp}°C\n"
           f"💧 <b>Влажность:</b> {humidity}%\n"
           f"💨 <b>Ветер:</b> {wind} м/с\n\n")

    elif weather.get('cod') == 404:
        await message.answer(f"❌ <b>Город '{city.capitalize()}' не найден!</b>\n\n"
                            "Проверьте правильность написания названия города.\n\n"
                            "🌍 <b>Используйте:</b> /weather Город")
    else:
        error_message = weather.get('message', 'Неизвестная ошибка')
        await message.answer(f"❌ <b>Ошибка:</b> {error_message}\n\n"
                            "🌍 <b>Используйте:</b> /weather Город")

@dp.message()
async def handle_message(message: Message):
    # Пропускаем команды и их аргументы
    if message.text.startswith('/'):
        return
    
    # Пропускаем пустые сообщения
    if not message.text.strip():
        return
    
    await message.answer("🌤️ <b>Я бот погоды!</b>\n\n"
                        "К сожалению, я умею только показывать погоду в любом городе мира.\n\n"
                        "🌍 <b>Используйте:</b> /weather Город")

@dp.startup()
async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Показать список команд"),
        BotCommand(command="weather", description="Узнать погоду в городе"),
    ])

async def main():
    try:
        await dp.start_polling(bot, polling_timeout=30)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        await bot.close()


if __name__ == "__main__":
    print("Бот запущен!")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен!")
        asyncio.run(bot.close())
        sys.exit()






