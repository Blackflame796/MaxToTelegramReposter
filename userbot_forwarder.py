import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from pymax import SocketMaxClient
from pymax.payloads import UserAgentPayload

load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
try:
    TG_CHAT_ID = int(os.getenv('TG_CHAT_ID', '0'))
except ValueError:
    TG_CHAT_ID = 0

MAX_PHONE = os.getenv('MAX_PHONE')

# Собираем список ID чатов для прослушивания (через запятую из .env или дефолтные)
raw_target_ids = os.getenv('TARGET_MAX_CHAT_ID', '-73072866554067, -77938496256712')
# Разбираем строку в множество очищенных от пробелов ID
TARGET_MAX_CHAT_IDS = {cid.strip() for cid in raw_target_ids.split(',') if cid.strip()}

ua = UserAgentPayload(device_type="DESKTOP", app_version="25.12.13")
client = SocketMaxClient(phone=MAX_PHONE, work_dir="cache", headers=ua)

bot = None


async def extract_sender_name(message) -> str:
    """Извлекает имя отправителя из сообщения или запрашивает его через API."""
    sender_obj = getattr(message, 'sender', None) or getattr(message, 'from_user', None) or getattr(message, 'author', None)
    
    # 1. Если объекта нет, пробуем запросить пользователя по ID
    if not sender_obj:
        user_id = (
            getattr(message, 'sender_id', None) 
            or getattr(message, 'from_id', None) 
            or getattr(message, 'user_id', None)
        )
        if user_id and hasattr(client, 'get_user'):
            try:
                sender_obj = await client.get_user(user_id)
            except Exception:
                pass

    # 2. Формируем имя из имеющихся полей
    if sender_obj:
        first_name = getattr(sender_obj, 'first_name', '') or ''
        last_name = getattr(sender_obj, 'last_name', '') or ''
        
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
            
        name = getattr(sender_obj, 'name', None) or getattr(sender_obj, 'title', None) or getattr(sender_obj, 'username', None)
        if name:
            return str(name)

    return "Пользователь"


@client.on_message()
async def handle_max_message(message):
    global bot
    try:
        chat_id = getattr(message, 'chat_id', None)
        if chat_id is None and hasattr(message, 'chat'):
            chat_id = getattr(message.chat, 'id', None)
            
        text = getattr(message, 'text', str(message))

        # Получаем имя отправителя
        sender = await extract_sender_name(message)

        print(f"[MAX] Сообщение от '{sender}' из чата {chat_id}: {text[:30]}...")

        # Проверяем, входит ли ID входящего чата в список прослушиваемых чатов
        if not TARGET_MAX_CHAT_IDS or str(chat_id) in TARGET_MAX_CHAT_IDS or "0" in TARGET_MAX_CHAT_IDS:
            if text and bot is not None:
                forward_text = f"<b>{sender}:</b>\n{text}"
                try:
                    await bot.send_message(chat_id=TG_CHAT_ID, text=forward_text)
                    print("-> Переслано в Telegram")
                except Exception as e:
                    print(f"-> Ошибка отправки в Telegram: {e}")

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")


async def main():
    global bot
    bot = Bot(
        token=TG_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    print("========================================")
    print(f"Запускаем клиента Max ({MAX_PHONE})...")
    print(f"Прослушиваемые чаты: {', '.join(TARGET_MAX_CHAT_IDS)}")
    print("========================================")
    
    await client.start()
    
    print("\nКлиент успешно подключен и слушает новые сообщения!")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())