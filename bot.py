import asyncio
import logging
import sqlite3
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Токен из настроек Render (Environment Variables)
BOT_TOKEN = os.getenv("8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI")

# ⚠️ ВСТАВЬ СЮДА ТОЧНЫЙ ID СВОЕЙ ГРУППЫ С МИНУСОМ (например: -1001234567890)
GROUP_CHAT_ID = -1001234567890 

# Ссылка на твой сайт загрузки на GitHub Pages
RESPACE_LINK = "https://github.io" 
RECLAMA_TEXT = f"Заходи на сайт! , И играй по настоящему ⚔️: {RESPACE_LINK}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация базы данных на постоянном диске /data
def init_db():
    conn = sqlite3.connect("/data/database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hashtag_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            topic_id TEXT,
            user_id TEXT,
            username TEXT,
            text TEXT,
            hashtags TEXT,
            date_saved TEXT
        )
    """)
    conn.commit()
    conn.close()

# 1. КОМАНДА /START РАБОТАЕТ СТРОГО В ЛС
@dp.message(CommandStart(), F.chat.type == "private")
async def cmd_start_private(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🌐 Перейти на сайт", 
        url=RESPACE_LINK
    ))
    await message.answer(
        text="Вы хотите войти через телеграмм на сайт.",
        reply_markup=builder.as_markup()
    )
    logging.info(f"Пользователь @{message.from_user.username} запустил бота в ЛС.")

# 2. ЧТЕНИЕ ХЕШТЕГОВ — РАБОТАЕТ СТРОГО В ГРУППАХ
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_messages(message: types.Message):
    if message.entities:
        found_hashtags = []
        for entity in message.entities:
            if entity.type == "hashtag":
                hashtag_text = message.text[entity.offset:entity.offset + entity.length]
                found_hashtags.append(hashtag_text)
        
        # Если нашли хештеги — пишем в базу данных
        if found_hashtags:
            conn = sqlite3.connect("/data/database.db")
            cursor = conn.cursor()
            
            chat_id = str(message.chat.id)
            topic_id = str(message.message_thread_id) if message.message_thread_id else "General"
            user_id = str(message.from_user.id)
            username = message.from_user.username if message.from_user.username else "No_Username"
            text_content = message.text
            hashtags_str = ", ".join(found_hashtags)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO hashtag_posts (chat_id, topic_id, user_id, username, text, hashtags, date_saved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (chat_id, topic_id, user_id, username, text_content, hashtags_str, now_str))
            
            conn.commit()
            conn.close()
            logging.info(f"Сохранен пост с хештегами {hashtags_str} от @{username}")

# 3. БЕСКОНЕЧНЫЙ ТАЙМЕР РЕКЛАМЫ В ГРУППУ (КАЖДЫЙ ЧАС)
async def promo_scheduler():
    while True:
        try:
            await bot.send_message(
                chat_id=GROUP_CHAT_ID, 
                text=RECLAMA_TEXT,
                message_thread_id=None # Строго в тему General
            )
            logging.info("Реклама сайта успешно отправлена в группу.")
        except Exception as e:
            logging.error(f"Ошибка при отправке рекламы: {e}")
        
        await asyncio.sleep(3600)

# Веб-сервер заглушки для Render
async def handle_web(request):
    return web.Response(text="Bot is running completely free!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    init_db()
    asyncio.create_task(promo_scheduler())
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
