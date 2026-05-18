import asyncio
import threading
import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types

# ==========================================
# 1. ЧАСТЬ ДЛЯ ОБХОДА (ВЕБ-СЕРВЕР)
# ==========================================
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is active!"}

def run_web_server():
    # Render требует именно порт 10000
    uvicorn.run(app, host="0.0.0.0", port=10000)

# Запускаем маскировочный веб-сервер в фоне
threading.Thread(target=run_web_server, daemon=True).start()


# ==========================================
# 2. ВАШ ОБЫЧНЫЙ ТЕЛЕГРАМ-БОТ
# ==========================================
# Вставьте ваш токен от BotFather вместо 'ВАШ_ТОКЕН'
bot = Bot(token='8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI')
dp = Dispatcher()

# Пример вашего хэндлера
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Привет! Я получил твое сообщение: {message.text}")

# Главная функция запуска aiogram
async def main():
    print("Telegram-бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
