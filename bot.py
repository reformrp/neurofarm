import asyncio
import threading
import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ===================================================
# 1. ЧАСТЬ ДЛЯ ОБХОДА БЛОКИРОВКИ RENDER (ВЕБ-СЕРВЕР)
# ===================================================
app = FastAPI()

# Главная страница, на которую будет заходить Cron-job
@app.get("/")
def read_root():
    return {"status": "Bot is successfully running 24/7!"}

def run_web_server():
    # Порт 10000 обязателен для Web Services на Render
    uvicorn.run(app, host="0.0.0.0", port=10000)

# Запускаем фоновый поток веб-сервера
threading.Thread(target=run_web_server, daemon=True).start()


# ===================================================
# 2. НАСТРОЙКА ТЕЛЕГРАМ-БОТА (AIOGRAM)
# ===================================================
# ТОКЕН: Вставьте ваш токен от BotFather вместо текста ниже (кавычки оставьте!)
BOT_TOKEN = "8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я успешно запущен на Render.\n"
        "Благодаря Cron-job я буду работать круглосуточно! 🚀"
    )

# Обработчик любых других текстовых сообщений (Эхо-бот)
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")


# Главная функция запуска всего приложения
async def main():
    print("Удаляем старые вебхуки (сброс конфликта с Google)...")
    # drop_pending_updates=True очистит очередь старых сообщений, чтобы бот не спамил при старте
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Запуск бесконечного опроса Telegram (Polling)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
