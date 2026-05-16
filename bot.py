import asyncio
import logging
import sqlite3
import os
import random
import time
from datetime import datetime, timedelta
import threading

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен вшит намертво для стабильности
BOT_TOKEN = "8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI"
GROUP_CHAT_ID = 0  

RESPAC_LINK = "https://github.io" 
RECLAMA_TEXT = f"🔥 Заходи на Форум REFORM RP! Наш сайт: {RESPAC_LINK}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hashtag_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, topic_id TEXT, 
            user_id TEXT, username TEXT, text TEXT, hashtags TEXT, date_saved TEXT
        )
    """)
    conn.commit()
    conn.close()

def clear_old_posts():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        one_day_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("DELETE FROM hashtag_posts WHERE date_saved < ?", (one_day_ago,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_random_day_news():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        one_day_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT username, text, hashtags FROM hashtag_posts WHERE date_saved >= ?", (one_day_ago,))
        posts = cursor.fetchall()
        conn.close()

        if not posts:
            return "📌 Новостей за последние 24 часа пока нет."

        random.shuffle(posts)
        selected_posts = posts[:3]

        response = "📰 *3 СЛУЧАЙНЫЕ НОВОСТИ ДНЯ REFORM RP:*\n\n"
        for i, post in enumerate(selected_posts, 1):
            username, text, hashtags = post
            short_text = text if len(text) < 150 else text[:147] + "..."
            response += f"{i}. 👤 *Автор:* @{username}\n💬 {short_text}\n🏷️ *Теги:* {hashtags}\n\n───────────────────\n\n"
        
        return response
    except Exception:
        return "❌ Произошла ошибка при загрузке новостей."

@dp.message(CommandStart(), F.chat.type == "private")
async def cmd_start_private(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🌐 Перейти на сайт", url=RESPAC_LINK))
    builder.row(types.InlineKeyboardButton(text="📰 Новости дня", callback_data="get_news_today"))
    await message.answer(text="Вы хотите войти через телеграмм на сайт.", reply_markup=builder.as_markup())

@dp.message(Command("news"), F.chat.type == "private")
async def cmd_news_private(message: types.Message):
    news_text = get_random_day_news()
    await message.answer(text=news_text, parse_mode="Markdown")

@dp.callback_query(F.data == "get_news_today")
async def cb_news_today(callback: types.CallbackQuery):
    news_text = get_random_day_news()
    await callback.message.answer(text=news_text, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_messages(message: types.Message):
    if message.entities:
        found_hashtags = []
        for entity in message.entities:
            if entity.type == "hashtag":
                hashtag_text = message.text[entity.offset:entity.offset + entity.length]
                found_hashtags.append(hashtag_text)
        
        if found_hashtags:
            conn = sqlite3.connect("database.db")
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

async def promo_scheduler():
    while True:
        if GROUP_CHAT_ID != 0:
            try:
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=RECLAMA_TEXT, message_thread_id=None)
            except Exception:
                pass
        clear_old_posts()
        await asyncio.sleep(3600)

# 🟢 ЖЕСТКИЙ КОСТЫЛЬ: Дисковая активность (I/O) каждые 10 секунд для обхода спячки
def run_disk_pinger():
    time.sleep(10)
    file_path = "bypass.tmp"
    while True:
        try:
            # 1. Записываем ровно 1 байт в файл
            with open(file_path, "wb") as f:
                f.write(b"1")
            
            # 2. Моментально удаляем файл с диска
            if os.path.exists(file_path):
                os.remove(file_path)
                
            # Выводим твой лаконичный статус в консоль Render
            print("ping", flush=True)
        except Exception:
            pass
        
        # Засыпаем строго на 10 секунд
        time.sleep(10)

async def main():
    init_db()
    clear_old_posts()
    asyncio.create_task(promo_scheduler())
    
    # Запускаем дисковый костыль-пингер в изолированном фоновом потоке
    pinger_thread = threading.Thread(target=run_disk_pinger, daemon=True)
    pinger_thread.start()
    
    # ИСПРАВЛЕНО: Принудительно очищаем старый зависший вебхук, чтобы бот снова начал мгновенно отвечать на сообщения в ЛС
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем чистый и быстрый Long Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
