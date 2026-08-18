import asyncio
import os
from dotenv import load_dotenv
from pymax import SocketMaxClient
from pymax.payloads import UserAgentPayload

# Загружаем переменные из .env
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
        chats = await client.get_chats()
        
        if not chats:
            print("Список чатов пуст или не удалось получить данные.")
            return

        print(f"Найдено чатов: {len(chats)}\n")
        
        # Форматированный вывод в консоль и подготовка для файла
        output_lines = []
        header = f"{'ID ЧАТА':<22} | {'ТИП':<12} | {'НАЗВАНИЕ / ИМЯ'}"
        divider = "=" * 65
        
        print(header)
        print(divider)
        
        output_lines.append(header)
        output_lines.append(divider)

        for c in chats:
            # Получаем ID чата
            c_id = getattr(c, 'id', None) or getattr(c, 'chat_id', 'Неизвестен')
            
            # Получаем название или имя
            title = getattr(c, 'title', None) or getattr(c, 'name', None)
            first_name = getattr(c, 'first_name', '')
            last_name = getattr(c, 'last_name', '')
            
            display_name = title or f"{first_name} {last_name}".strip() or "Без названия"
            chat_type = str(getattr(c, 'type', '—'))

            line = f"{str(c_id):<22} | {chat_type:<12} | {display_name}"
            print(line)
            output_lines.append(line)

        print(divider)

        # Сохранение результатов в txt файл
        with open("my_chats.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
            
        print("\nПолный список также успешно сохранен в файл 'my_chats.txt'")

    except Exception as e:
        print(f"Произошла ошибка при получении чатов: {e}")


if __name__ == "__main__":
    asyncio.run(main())