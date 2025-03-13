## TG_AI_Bitrix24

### Документация по проекту: Интеграция Telegram-бота с Bitrix24

### 1. Установка
### 1.1. Требования

Для работы проекта потребуется:

* Python версии 3.8 или выше
* Установленный pip для установки зависимостей
* Доступ к API Bitrix24 (API-ключ)

### 1.2. Установка зависимостей

1. Склонируйте репозиторий проекта:
   </br>`git clone https://your-repository-url.git cd your-repository-directory`

2. Установите зависимости:
   </br>`pip install -r requirements.txt`

### 1.3. Конфигурация окружения

1. Настройка конфигурации: В корневом каталоге проекта создайте файл .env и добавьте следующие параметры:

`BITRIX24_API_KEY=your_bitrix24_api_key`
</br>`BITRIX24_DOMAIN=https://your-bitrix24-domain.bitrix24.ru `
</br>`TELEGRAM_BOT_API_TOKEN=your_telegram_bot_api_token `
</br>`DATABASE_URL=postgres://user:password@localhost:5432/database_name`

Замените значения на соответствующие данные для вашего проекта:

* `BITRIX24_API_KEY` — ваш API-ключ для Bitrix24.
* `BITRIX24_DOMAIN` — домен вашего Bitrix24.
* `TELEGRAM_BOT_API_TOKEN` — токен вашего Telegram-бота.
* `DATABASE_URL` — строка подключения к базе данных PostgreSQL.

**Создание базы данных:** Если база данных еще не создана, создайте ее с помощью SQL-запроса:
</br>`CREATE DATABASE your_database_name;`

**Применение миграций:** В случае наличия миграций в проекте, выполните их:
</br>`alembic upgrade head`

## 2. Настройка

### 2.1. Настройка Telegram-бота

1. Перейдите в [BotFather]() и создайте нового бота.
2. Получите API токен для вашего бота.
3. Укажите его в переменной окружения `TELEGRAM_BOT_API_TOKEN`.

### 2.2. Настройка Bitrix24

1. Создайте новый API-ключ для вашего Bitrix24.
2. Укажите ключ в переменной окружения BITRIX24_API_KEY.
3. Убедитесь, что у вас есть доступ к CRM в Bitrix24 и настройте соответствующие модули (например, "Контакты", "
   Сделки").

### 2.3. Настройка базы данных

1. Убедитесь, что PostgreSQL установлен на вашем сервере или локальной машине.
2. Создайте пользователя и базу данных для
   проекта: </br>`CREATE USER your_user WITH PASSWORD 'your_password';` </br>`CREATE DATABASE your_database_name;` </br>`ALTER DATABASE your_database_name OWNER TO your_user;`
3. Установите соединение с базой данных, добавив строку подключения в `.env`:
   </br>`DATABASE_URL=postgres://your_user:your_password@localhost:5432/your_database_name`

## 3. API

### 3.1. API для работы с Bitrix24

1. **Создание контакта:** API для создания контакта в Bitrix24:
   </br> `def create_contact_in_bitrix(name, phone, email, address):` # Отправка запроса на создание контакта


2. **Поиск контакта по телефону:** API для поиска контакта по номеру телефона:
   </br>`def get_contact_id_by_phone(phone):` # Отправка запроса на поиск контакта


3. **Создание сделки:** API для создания сделки:
   </br>`def create_deal_in_bitrix(title, contact_id, opportunity):` # Отправка запроса на создание сделки


4. **Обновление сделки:** API для обновления существующей сделки:
   </br>`def update_deal_in_bitrix(title, deal_id, opportunity):` # Отправка запроса на обновление сделки


5. **Отправка сообщений в чат:** API для отправки сообщений в чат с клиентом:
   </br> `def send_chat_to_bitrix(contact_id, message):` # Отправка сообщения в чат

## 4. База данных 
В проекте используются две таблицы в базе данных PostgreSQL: users и survey_responses. Эти таблицы хранят информацию о пользователях и их ответах на анкеты.

### 4.1. Структура базы данных 
**Таблица** `users`: Таблица хранит информацию о пользователях бота.

* `user_id` — уникальный ID пользователя в Telegram (должен быть уникальным).
* `username` — имя пользователя в Telegram.
* `full_name` — полное имя пользователя.
* `category` — категория пользователя (может быть значением 'Компания' или 'Частное лицо').
* `created_at` — дата и время создания записи пользователя (по умолчанию — текущее время).

**Таблица** `survey_responses`: Хранит ответы пользователей на вопросы анкеты.

* `user_id` — ссылка на user_id из таблицы users. Обеспечивает связь между пользователем и его ответами. При удалении пользователя, все его ответы также будут удалены.
* `name` — имя пользователя, который заполнил анкету.
* `phone` — номер телефона пользователя.
* `email` — email пользователя.
* `address` — адрес пользователя.
* `furniture_type` — тип мебели, интересующий пользователя.
* `design_interest` — интересы в дизайне (например, стиль, предпочтения).
* `budget` — бюджет пользователя.
* `delivery` — предпочтения по доставке.
* `company_name` — название компании (если пользователь — компания).
* `cooperation` — предпочтения в сотрудничестве.
* `created_at` — дата и время создания записи (по умолчанию — текущее время).

Таблица chat_history: Хранит историю переписки.

message_id — уникальный ID сообщения. user_id — ссылка на таблицу users. message — текст сообщения. sender —
отправитель (пользователь/бот).

## 5. Использование 
### 5.1. Запуск бота

1. Для запуска бота используйте следующую команду: `python main.py`

### 5.2. Отправка сообщения в Bitrix24 
1. После получения сообщения от пользователя в боте, бот автоматически сохраняет сообщение и отправляет его в Bitrix24.

### 5.3. Обработка анкеты 
1. Бот предлагает пользователю анкеты и сохраняет ответы. 
2. Ответы пользователя сохраняются в базе данных и могут быть отправлены в Bitrix24.

## 6. Примечания 
* Убедитесь, что все ключи и токены для Bitrix24 и Telegram бота корректны. 
* В случае проблем с API Bitrix24, проверьте правильность API-ключа и прав доступа. 
* Вы можете расширить функциональность бота, добавив дополнительные функции для работы с другими модулями Bitrix24.
