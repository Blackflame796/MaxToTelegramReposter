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

    await client.start()
    print("Успешное подключение!\n")

    try:
        # 1. Пробуем получить список диалогов/чатов через get_dialogs()
        dialogs = []
        if hasattr(client, 'get_dialogs'):
            dialogs = await client.get_dialogs()
        elif hasattr(client, 'get_chats_list'):
            dialogs = await client.get_chats_list()

        if not dialogs:
            print("Не удалось автоматически получить диалоги или список пуст.")
            return

        output_lines = []
        header = f"{'ID ЧАТА':<22} | {'ТИП/СТАТУС':<12} | {'НАЗВАНИЕ / ИМЯ'}"
        divider = "=" * 65

        print(header)
        print(divider)
        output_lines.extend([header, divider])

        for item in dialogs:
            # Извлекаем объект чата/пользователя из структуры диалога
            chat_obj = getattr(item, 'chat', item)
            
            c_id = getattr(chat_obj, 'id', None) or getattr(chat_obj, 'chat_id', 'Неизвестен')
            
            title = getattr(chat_obj, 'title', None) or getattr(chat_obj, 'name', None)
            first_name = getattr(chat_obj, 'first_name', '')
            last_name = getattr(chat_obj, 'last_name', '')
            
            display_name = title or f"{first_name} {last_name}".strip() or "Без названия"
            chat_type = str(getattr(chat_obj, 'type', '—'))

            line = f"{str(c_id):<22} | {chat_type:<12} | {display_name}"
            print(line)
            output_lines.append(line)

        print(divider)

        with open("my_chats.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        print("\nСписок сохранен в файл 'my_chats.txt'")

    except Exception as e:
        print(f"Произошла ошибка при получении чатов: {e}")


if __name__ == "__main__":
    asyncio.run(main())