import asyncio
import os
from dotenv import load_dotenv
from pymax import SocketMaxClient
from pymax.payloads import UserAgentPayload

load_dotenv()

MAX_PHONE = os.getenv('MAX_PHONE')
INVITE_LINK = "https://max.ru/join/U2MW3iXqOG_1iMS0Rn0jD4QCbvUgZwBpWus9bboheGc"

ua = UserAgentPayload(device_type="DESKTOP", app_version="25.12.13")
client = SocketMaxClient(phone=MAX_PHONE, work_dir="cache", headers=ua)


async def get_chat_id_from_link(link: str):
    await client.start()
    
    # Извлекаем хэш инвайта из конца ссылки
    invite_hash = link.split('/')[-1].replace("join?", "").replace("invite=", "")
    print(f"Обработка хэша: {invite_hash}\n")

    try:
        # Пробуем получить информацию о чате по ссылке/хэшу
        # В зависимости от версии pymax метод может называться get_chat_by_invite, resolve_invite или get_chat
        chat_info = None
        
        if hasattr(client, 'get_chat_by_invite'):
            chat_info = await client.get_chat_by_invite(invite_hash)
        elif hasattr(client, 'resolve_invite'):
            chat_info = await client.resolve_invite(invite_hash)
        elif hasattr(client, 'get_chat'):
            chat_info = await client.get_chat(link)
            
        if chat_info:
            chat_id = getattr(chat_info, 'id', getattr(chat_info, 'chat_id', 'Не найден'))
            title = getattr(chat_info, 'title', getattr(chat_info, 'name', 'Без названия'))
            
            print("================ РЕЗУЛЬТАТ ================")
            print(f"Название чата: {title}")
            print(f"TARGET_MAX_CHAT_ID: {chat_id}")
            print("===========================================")
            return chat_id
        else:
            print("Метод резолва вернул пустой ответ. Проверьте валидность ссылки.")

    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")


if __name__ == "__main__":
    asyncio.run(get_chat_id_from_link(INVITE_LINK))