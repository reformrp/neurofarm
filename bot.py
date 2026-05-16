import asyncio
import logging
import sqlite3
import os
import random
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import TokenBasedRequestHandler, setup_application

BOT_TOKEN = "8815834719:AAEE6D_m4F8k7mG90zM"
GROUP_CHAT_ID = 0  

RESPAC_LINK = "https://github.io" 
RECLAMA_TEXT = f"🔥 Заходи играть на REFORM RP! Наш сайт загрузки: {RESPAC_LINK}"

RENDER_URL = "https://onrender.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

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
        if not posts: return "📌 Новостей за последние 24 часа пока нет."
        random.shuffle(posts)
        selected_posts = posts[:3]
        response = "📰 *3 СЛУЧАЙНЫЕ НОВОСТИ ДНЯ REFORM RP:*\n\n"
        for i, post in enumerate(selected_posts, 1):
            username, text, hashtags = post
            short_text = text if len(text) < 150 else text[:147] + "..."
            response += f"{i}. 👤 *Автор:* @{username}\n💬 {short_text}\n🏷️ *Теги:* {hashtags}\n\n"
            response += "───────────────────\n\n"
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

async def promo_scheduler(bot: Bot):
    while True:
        if GROUP_CHAT_ID != 0:
            try:
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=RECLAMA_TEXT, message_thread_id=None)
            except Exception:
                pass
        clear_old_posts()
        await asyncio.sleep(3600)

async def on_startup(bot: Bot):
    init_db()
    clear_old_posts()
    # Установка вебхука в Telegram
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Вэбхук установлен: {WEBHOOK_URL}")
    asyncio.create_task(promo_scheduler(bot))

def main():
    app = web.Application()
    
    # Главная страница для логов Render
    async def handle_root(request):
        print("ping", flush=True)
        return web.Response(text="Bot is Live!")
    app.router.add_get('/', handle_root)

    # Использование стабильного TokenBasedRequestHandler для aiogram 3
    handler = TokenBasedRequestHandler(dispatcher=dp)
    handler.register(app, path="/webhook/{bot_token}")
    
    setup_application(app, dp, bot=bot)
    app.on_startup.append(lambda _: on_startup(bot))

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
import asyncio
import logging
import sqlite3
import os
import random
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import TokenBasedRequestHandler, setup_application

BOT_TOKEN = "8815834719:AAEE6D_m4F8k7mG90zM"
GROUP_CHAT_ID = 0  

RESPAC_LINK = "https://github.io" 
RECLAMA_TEXT = f"🔥 Заходи играть на REFORM RP! Наш сайт загрузки: {RESPAC_LINK}"

RENDER_URL = "https://onrender.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

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
        if not posts: return "📌 Новостей за последние 24 часа пока нет."
        random.shuffle(posts)
        selected_posts = posts[:3]
        response = "📰 *3 СЛУЧАЙНЫЕ НОВОСТИ ДНЯ REFORM RP:*\n\n"
        for i, post in enumerate(selected_posts, 1):
            username, text, hashtags = post
            short_text = text if len(text) < 150 else text[:147] + "..."
            response += f"{i}. 👤 *Автор:* @{username}\n💬 {short_text}\n🏷️ *Теги:* {hashtags}\n\n"
            response += "───────────────────\n\n"
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

async def promo_scheduler(bot: Bot):
    while True:
        if GROUP_CHAT_ID != 0:
            try:
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=RECLAMA_TEXT, message_thread_id=None)
            except Exception:
                pass
        clear_old_posts()
        await asyncio.sleep(3600)

async def on_startup(bot: Bot):
    init_db()
    clear_old_posts()
    # Установка вебхука в Telegram
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Вэбхук установлен: {WEBHOOK_URL}")
    asyncio.create_task(promo_scheduler(bot))

def main():
    app = web.Application()
    
    # Главная страница для логов Render
    async def handle_root(request):
        print("ping", flush=True)
        return web.Response(text="Bot is Live!")
    app.router.add_get('/', handle_root)

    # Использование стабильного TokenBasedRequestHandler для aiogram 3
    handler = TokenBasedRequestHandler(dispatcher=dp)
    handler.register(app, path="/webhook/{bot_token}")
    
    setup_application(app, dp, bot=bot)
    app.on_startup.append(lambda _: on_startup(bot))

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
