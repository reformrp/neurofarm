import asyncio
import threading
import uvicorn
import urllib.request  # Добавили стандартную библиотеку для быстрого запроса
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ТОКЕН: Вставьте ваш токен от BotFather вместо текста ниже (кавычки оставьте!)
BOT_TOKEN = "8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI"

# ===================================================
# ЖЕСТКИЙ СБРОС ВЕБХУКА ПЕРЕД СТАРТОМ (ФИКС ОШИБКИ)
# ===================================================
print("Принудительно очищаем старый вебхук в Telegram...")
try:
    # Запрос напрямую к серверам Telegram без участия aiogram
    url = f"https://telegram.org{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True"
    urllib.request.urlopen(url)
    print("Вебхук успешно стерт! Путь для Polling открыт.")
except Exception as e:
    print(f"Не удалось стереть вебхук через urllib: {e}")

# ===================================================
# 1. ЧАСТЬ ДЛЯ ОБХОДА БЛОКИРОВКИ RENDER (ВЕБ-СЕРВЕР)
# ===================================================
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is successfully running 24/7!"}

def run_web_server():
    uvicorn.run(app, host="0.0.0.0", port=10000)

threading.Thread(target=run_web_server, daemon=True).start()

# ===================================================
# 2. НАСТРОЙКА ТЕЛЕГРАМ-БОТА (AIOGRAM)
# ===================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я успешно запущен на Render и работаю 24/7! 🚀")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")

async def main():
    print("Запуск бесконечного опроса Telegram (Polling)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
