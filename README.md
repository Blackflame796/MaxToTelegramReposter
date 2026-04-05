# MaxToTelegram Forwarder

Скрипт-юзербот для пересылки сообщений из корпоративного мессенджера **Max** в указанный **Telegram**-чат (ЛС, группу или канал) с использованием библиотеки `pymax` и `aiogram`.

## Требования
- Python 3.10+
- Зарегистрированный бот в Telegram (получить токен можно у @BotFather)
- Зарегистрированный аккаунт в мессенджере Max
- Установленные зависимости

## Установка и запуск (Деплой)

### 1. Подготовка окружения

Создайте виртуальное окружение и установите все необходимые библиотеки:

```bash
# Создание виртуального окружения
python -m venv .venv

# Активация окружения (в Windows используйте .venv\Scripts\activate)
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации

В корневой директории проекта теперь можно использовать файл конфигурации окружения. Создайте файл `.env` (если его нет) со следующим содержимым:

```env
# Ваш Telegram-бот
TG_TOKEN=123456789:AAH...
# ID целевого чата Telegram
TG_CHAT_ID=-100123456789

# Ваш номер телефона от профиля Max
MAX_PHONE=+79xxxxxxxxx
# (Опционально) ID группы, из которой будем пересылать (оставьте пустым или настройте фильтр в python-коде)
TARGET_MAX_CHAT_ID=-73xxxxxxxxxx
```

### 3. Авторизация (первый запуск)

При первом запуске клиенту Max потребуется сохранить сессию и авторизоваться. Обычный запуск:

```bash
python userbot_forwarder.py
```
> [!IMPORTANT]
> При первом запуске смотрите на вывод терминала — возможно, потребуется ввести код из приложения Max! После успешного входа создастся папка `cache/`, в которой будет храниться сессия.

---

## Варианты фонового деплоя на сервере

Чтобы скрипт работал 24/7, не зависел от того, закрыли ли вы консоль, и перезапускался в случае ошибки, рекомендуем использовать **Systemd** (для Linux).

### Настройка Systemd

1. Откройте файл демона на создание:
   ```bash
   sudo nano /etc/systemd/system/maxtotg.service
   ```
2. Вставьте конфигурацию (не забудьте поменять `WorkingDirectory`, пути к python и `User` на свои):
   ```ini
   [Unit]
   Description=MaxToTelegram Bot Forwarder
   After=network.target

   [Service]
   User=ваше_имя_пользователя
   WorkingDirectory=/путь/к/проекту/MaxToTelegram
   Environment="PATH=/путь/к/проекту/MaxToTelegram/.venv/bin"
   ExecStart=/путь/к/проекту/MaxToTelegram/.venv/bin/python userbot_forwarder.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
3. Сохраните файл, перезапустите демоны и включите автозагрузку:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable maxtotg.service
   sudo systemctl start maxtotg.service
   ```
4. **Просмотр логов:**
   ```bash
   sudo journalctl -u maxtotg.service -v -f
   ```