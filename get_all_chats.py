import asyncio
import os
from dotenv import load_dotenv
from pymax import SocketMaxClient
from pymax.payloads import UserAgentPayload

load_dotenv()

MAX_PHONE = os.getenv('MAX_PHONE')
TARGET_MAX_CHAT_ID = os.getenv('TARGET_MAX_CHAT_ID', '-73072866554067')

ua = UserAgentPayload(device_type="DESKTOP", app_version="25.12.13")
client = SocketMaxClient(phone=MAX_PHONE, work_dir="cache", headers=ua)


async def main():
    print("========================================")
    print(f"Подключение к Max ({MAX_PHONE})...")
    print("========================================")

    start_task = asyncio.create_task(client.start())
    await asyncio.sleep(4)  # Ждем завершения синхронизации

    try:
        found_chats = {}

        # 1. Собираем диалоги и чаты из всех внутренних структур
        sources = [
            getattr(client, 'chats', None),
            getattr(client, 'dialogs', None),
            getattr(client, '_chats', None),
            getattr(client, '_dialogs', None),
        ]

        for source in sources:
            if not source:
                continue
            items = source.values() if isinstance(source, dict) else source
            for item in items:
                # Извлекаем вложенный объект чата или используем сам объект
                chat_obj = getattr(item, 'chat', item)
                
                c_id = getattr(chat_obj, 'id', None) or getattr(chat_obj, 'chat_id', None)
                if c_id is None:
                    continue

                title = getattr(chat_obj, 'title', None) or getattr(chat_obj, 'name', None)
                first_name = getattr(chat_obj, 'first_name', '')
                last_name = getattr(chat_obj, 'last_name', '')
                display_name = title or f"{first_name} {last_name}".strip() or "Без названия"
                chat_type = str(getattr(chat_obj, 'type', '—'))

                found_chats[str(c_id)] = (chat_type, display_name)

        # 2. Если группы нет в кэше, делаем точечный запрос целевой группы
        if TARGET_MAX_CHAT_ID and str(TARGET_MAX_CHAT_ID) not in found_chats:
            try:
                if hasattr(client, 'get_chat'):
                    target_obj = await client.get_chat(int(TARGET_MAX_CHAT_ID))
                    t_title = getattr(target_obj, 'title', getattr(target_obj, 'name', 'Целевая группа'))
                    found_chats[str(TARGET_MAX_CHAT_ID)] = ("GROUP", t_title)
            except Exception:
                pass

        header = f"{'ID ЧАТА':<22} | {'ТИП':<18} | {'НАЗВАНИЕ / ИМЯ'}"
        divider = "=" * 70
        print("\n" + header)
        print(divider)

        output_lines = [header, divider]
        for c_id, (c_type, c_name) in found_chats.items():
            # Помечаем целевую группу
            mark = " [TARGET]" if str(c_id) == str(TARGET_MAX_CHAT_ID) else ""
            line = f"{str(c_id):<22} | {c_type:<18} | {c_name}{mark}"
            print(line)
            output_lines.append(line)

        print(divider)

        with open("my_chats.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
            
        print("\nРезультат сохранен в 'my_chats.txt'")

    except Exception as e:
        print(f"Ошибка при обработке: {e}")
    finally:
        start_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())