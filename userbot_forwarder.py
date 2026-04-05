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
TARGET_MAX_CHAT_ID = os.getenv('TARGET_MAX_CHAT_ID', '-73072866554067') # ID вашей частной группы

ua = UserAgentPayload(device_type="DESKTOP", app_version="25.12.13")
client = SocketMaxClient(phone=MAX_PHONE, work_dir="cache", headers=ua)

bot = None


@client.on_message()
async def handle_max_message(message):
    global bot
    try:
        chat_id = getattr(message, 'chat_id', None)
        if chat_id is None and hasattr(message, 'chat'):
            chat_id = getattr(message.chat, 'id', None)
        text = getattr(message, 'text', str(message))

        sender = "Кто-то"
        if hasattr(message, 'sender') and message.sender:
            sender = getattr(message.sender, 'first_name', "Пользователь")

        print(f"[MAX] Новое сообщение из чата {chat_id}: {text[:30]}...")

        if TARGET_MAX_CHAT_ID == "0" or not TARGET_MAX_CHAT_ID or str(chat_id) == str(TARGET_MAX_CHAT_ID):
            if text and bot is not None:
                forward_text = f"<b>{sender}:</b>\n{text}"
                try:
                    await bot.send_message(chat_id=TG_CHAT_ID, text=forward_text)
                    print(f"-> Переслано в Telegram")
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
    print("========================================")
    print("ВАЖНО: При первом запуске в этой консоли может потребоваться ввести код подтверждения.")
    
    await client.start()
    
    print("\nКлиент успешно подключен и слушает новые сообщения!")
    print("Получение списка доступных чатов...\n")
    
    try:
        chats = await client.get_chats()
        print("================ СПИСОК ЧАТОВ ================")
        for c in chats:
            c_id = getattr(c, 'id', 'Неизвестен')
            name = getattr(c, 'title', getattr(c, 'name', getattr(c, 'first_name', 'Без имени')))
            print(f"ID: {c_id} | Имя: {name}")
        print("==============================================\n")
    except Exception as e:
        print(f"Не удалось получить список чатов: {e}")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
