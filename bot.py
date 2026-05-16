import asyncio
import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F

# ТОКЕН И ID ГРУППЫ (Токен лучше скрыть в настройки хостинга, а ID вписать сюда)
BOT_TOKEN = "8815834719:AAFIU8hOYNWXF35I1xGL1A4E_4Vro1Jp9UI"
# ID твоей группы (обязательно с минусом в начале, например: -100123456789)
GROUP_CHAT_ID = -1000000000000 
# Текст рекламы твоего сайта
RESPACE_LINK = "https://github.io" 
RECLAMA_TEXT = f" Заходи на сайт! , И играй по настоящему ⚔️: {RESPACE_LINK}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция инициализации базы данных SQLite
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

# Хендлер, который ловит ВСЕ сообщения в группе
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_messages(message: types.Message):
    # Проверяем, есть ли в сообщении сущности (entities) и ищем среди них хештеги
    if message.entities:
        found_hashtags = []
        for entity in message.entities:
            if entity.type == "hashtag":
                # Вырезаем сам текст хештега из сообщения
                hashtag_text = message.text[entity.offset:entity.offset + entity.length]
                found_hashtags.append(hashtag_text)
        
        # Если нашли хотя бы один хештег — сохраняем пост в БД
        if found_hashtags:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            
            # Собираем данные
            chat_id = str(message.chat.id)
            # Если в группе есть темы, message.message_thread_id покажет id топика
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

# Бесконечный таймер для отправки рекламы каждый час
async def promo_scheduler():
    while True:
        try:
            # Чтобы отправить строго в General (Основную тему) супергруппы, 
            # нужно передать message_thread_id=None или id первой главной темы (обычно это 1)
            await bot.send_message(
                chat_id=GROUP_CHAT_ID, 
                text=RECLAMA_TEXT,
                message_thread_id=None 
            )
            logging.info("Реклама сайта успешно отправлена в General.")
        except Exception as e:
            logging.error(f"Ошибка при отправке рекламы: {e}")
        
        # Ждем 3600 секунд (1 час) перед следующим разом
        await asyncio.sleep(3600)

async def main():
    init_db()
    # Запускаем фоновую задачу таймера рекламы, чтобы она не мешала боту читать чат
    asyncio.create_task(promo_scheduler())
    # Запускаем бесконечный опрос серверов ТГ (Long Polling)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
