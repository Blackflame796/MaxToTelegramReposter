import asyncio
import os
from dotenv import load_dotenv
from pymax import SocketMaxClient
from pymax.payloads import UserAgentPayload

load_dotenv()

MAX_PHONE = os.getenv('MAX_PHONE')

if not MAX_PHONE:
    print("ОШИБКА: Задайте MAX_PHONE в файле .env")
    exit(1)

ua = UserAgentPayload(device_type="DESKTOP", app_version="25.12.13")
client = SocketMaxClient(phone=MAX_PHONE, work_dir="cache", headers=ua)


async def main():
    print("========================================")
    print(f"Подключение к Max ({MAX_PHONE})...")
    print("========================================")

    # Запускаем клиент в фоновой задаче, чтобы он не блокировал скрипт
    start_task = asyncio.create_task(client.start())
    
    # Ждем 3 секунды, чтобы завершилась синхронизация (Sync completed)
    await asyncio.sleep(3)
    print("Успешное подключение и синхронизация!\n")

    try:
        # Извлекаем синхронизированные диалоги из локального хранилища клиента
        dialogs = []
        
        if hasattr(client, 'dialogs') and client.dialogs:
            dialogs = list(client.dialogs.values()) if isinstance(client.dialogs, dict) else client.dialogs
        elif hasattr(client, 'chats') and client.chats:
            dialogs = list(client.chats.values()) if isinstance(client.chats, dict) else client.chats

        if not dialogs:
            print("Внимание: хранилище пусто. Пробуем альтернативный доступ...")
            # Запасной вариант обращения к кэшу
            if hasattr(client, '_dialogs'):
                dialogs = list(client._dialogs.values())

        if not dialogs:
            print("Не удалось прочитать список из кэша.")
            return

        output_lines = []
        header = f"{'ID ЧАТА':<22} | {'ТИП':<10} | {'НАЗВАНИЕ / ИМЯ'}"
        divider = "=" * 65

        print(header)
        print(divider)
        output_lines.extend([header, divider])

        for item in dialogs:
            # Извлекаем объект чата или юзера из элемента диалога
            chat_obj = getattr(item, 'chat', item)
            user_obj = getattr(item, 'user', None)
            
            # Определяем ID
            c_id = (
                getattr(chat_obj, 'id', None) 
                or getattr(chat_obj, 'chat_id', None)
                or getattr(item, 'id', 'Неизвестен')
            )
            
            # Определяем Название / Имя
            title = getattr(chat_obj, 'title', None) or getattr(chat_obj, 'name', None)
            
            first_name = getattr(user_obj or chat_obj, 'first_name', '')
            last_name = getattr(user_obj or chat_obj, 'last_name', '')
            user_full_name = f"{first_name} {last_name}".strip()
            
            display_name = title or user_full_name or getattr(chat_obj, 'username', None) or "Без названия"
            chat_type = str(getattr(chat_obj, 'type', 'GROUP' if title else 'USER'))

            line = f"{str(c_id):<22} | {chat_type:<10} | {display_name}"
            print(line)
            output_lines.append(line)

        print(divider)

        with open("my_chats.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        print("\nСписок сохранен в файл 'my_chats.txt'")

    except Exception as e:
        print(f"Ошибка при чтении списка: {e}")
    finally:
        # Отменяем фоновую задачу клиента перед выходом
        start_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())