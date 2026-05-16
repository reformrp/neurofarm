import asyncio
import logging
import sqlite3
import os
import random
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Считываем токен скрытый в настройках Render (Environment)
BOT_TOKEN = os.getenv("8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI")
GROUP_CHAT_ID = 0  

RESPAC_LINK = "https://github.io" 
RECLAMA_TEXT = f"Заходи на сайт! , И играй по настоящему ⚔️: {RESPAC_LINK}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("database.db")
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

def clear_old_posts():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        one_day_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("DELETE FROM hashtag_posts WHERE date_saved < ?", (one_day_ago,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()
        if deleted_rows > 0:
            logging.info(f"Очистка БД: успешно удалено {deleted_rows} устаревших постов.")
    except Exception as e:
        logging.error(f"Ошибка при очистке базы данных: {e}")

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
            response += f"{i}. 👤 *Автор:* @{username}\n💬 {short_text}\n🏷️ *Теги:* {hashtags}\n\n"
            response += "───────────────────\n\n"
        
        return response
    except Exception as e:
        logging.error(f"Ошибка при выборке новостей: {e}")
        return "❌ Произошла ошибка при загрузке новостей."

@dp.message(CommandStart(), F.chat.type == "private")
async def cmd_start_private(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🌐 Перейти на сайт", url=RESPAC_LINK))
    builder.row(types.InlineKeyboardButton(text="📰 Новости дня", callback_data="get_news_today"))
    
    await message.answer(
        text="Вы хотите войти через телеграмм на сайт.",
        reply_markup=builder.as_markup()
    )

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
            logging.info(f"Сохранен пост с хештегами {hashtags_str} от @{username}")

async def promo_scheduler():
    while True:
        if GROUP_CHAT_ID != 0:
            try:
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=RECLAMA_TEXT, message_thread_id=None)
                logging.info("Реклама сайта успешно отправлена в группу.")
            except Exception as e:
                logging.error(f"Ошибка рассылки: {e}")
        clear_old_posts()
        await asyncio.sleep(3600)

# Простейший нативный веб-сервер для прохождения проверок Render
class WebStubHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Bot is running perfectly free!".encode("utf-8"))
    def log_message(self, format, *args):
        return # Отключаем спам логов веб-сервера в консоль

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebStubHandler)
    logging.info(f"Нативный веб-сервер запущен на порту {port}")
    server.serve_forever()

async def main():
    init_db()
    clear_old_posts()
    asyncio.create_task(promo_scheduler())
    
    # Запускаем нативный веб-сервер в отдельном изолированном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
