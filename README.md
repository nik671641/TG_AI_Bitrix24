# TG_AI_Bitrix24

Документация по проекту: Интеграция Telegram-бота с Bitrix24
1. Установка
1.1. Требования
   
Для работы проекта потребуется:
Python версии 3.8 или выше
Установленный pip для установки зависимостей
Доступ к API Bitrix24 (API-ключ)

1.2. Установка зависимостей

Склонируйте репозиторий проекта:
git clone https://your-repository-url.git
cd your-repository-directory

Установите зависимости:
pip install -r requirements.txt

1.3. Конфигурация окружения
Настройка конфигурации: В корневом каталоге проекта создайте файл .env и добавьте следующие параметры:

BITRIX24_API_KEY=your_bitrix24_api_key
BITRIX24_DOMAIN=https://your-bitrix24-domain.bitrix24.ru
TELEGRAM_BOT_API_TOKEN=your_telegram_bot_api_token
DATABASE_URL=postgres://user:password@localhost:5432/database_name

Замените значения на соответствующие данные для вашего проекта:
BITRIX24_API_KEY — ваш API-ключ для Bitrix24.
BITRIX24_DOMAIN — домен вашего Bitrix24.
TELEGRAM_BOT_API_TOKEN — токен вашего Telegram-бота.
DATABASE_URL — строка подключения к базе данных PostgreSQL.

Создание базы данных: Если база данных еще не создана, создайте ее с помощью SQL-запроса:
CREATE DATABASE your_database_name;

Применение миграций: В случае наличия миграций в проекте, выполните их:
alembic upgrade head

2. Настройка
2.1. Настройка Telegram-бота
Перейдите в BotFather и создайте нового бота.
Получите API токен для вашего бота.
Укажите его в переменной окружения TELEGRAM_BOT_API_TOKEN.

2.2. Настройка Bitrix24
Создайте новый API-ключ для вашего Bitrix24.
Укажите ключ в переменной окружения BITRIX24_API_KEY.
Убедитесь, что у вас есть доступ к CRM в Bitrix24 и настройте соответствующие модули (например, "Контакты", "Сделки").

2.3. Настройка базы данных
Убедитесь, что PostgreSQL установлен на вашем сервере или локальной машине.

Создайте пользователя и базу данных для проекта:
CREATE USER your_user WITH PASSWORD 'your_password';
CREATE DATABASE your_database_name;
ALTER DATABASE your_database_name OWNER TO your_user;

Установите соединение с базой данных, добавив строку подключения в .env:
DATABASE_URL=postgres://your_user:your_password@localhost:5432/your_database_name

3. API
3.1. API для работы с Bitrix24

Создание контакта: API для создания контакта в Bitrix24:
def create_contact_in_bitrix(name, phone, email, address):
    # Отправка запроса на создание контакта

Поиск контакта по телефону: API для поиска контакта по номеру телефона:
def get_contact_id_by_phone(phone):
    # Отправка запроса на поиск контакта

Создание сделки: API для создания сделки:
def create_deal_in_bitrix(title, contact_id, opportunity):
    # Отправка запроса на создание сделки

Обновление сделки: API для обновления существующей сделки:
def update_deal_in_bitrix(title, deal_id, opportunity):
    # Отправка запроса на обновление сделки

Отправка сообщений в чат: API для отправки сообщений в чат с клиентом:
def send_chat_to_bitrix(contact_id, message):
    # Отправка сообщения в чат
    
4. База данных
4.1. Структура базы данных
Таблица users: Хранит информацию о пользователях бота.

user_id — уникальный ID пользователя.
name — имя пользователя.
phone — телефонный номер.
email — email адрес.
address — адрес.
Таблица survey_responses: Хранит ответы пользователей на вопросы анкеты.

response_id — уникальный ID ответа.
user_id — ссылка на таблицу users.
question — вопрос анкеты.
answer — ответ пользователя.
Таблица chat_history: Хранит историю переписки.

message_id — уникальный ID сообщения.
user_id — ссылка на таблицу users.
message — текст сообщения.
sender — отправитель (пользователь/бот).

5. Использование
5.1. Запуск бота

Для запуска бота используйте следующую команду:
python main.py

5.2. Отправка сообщения в Bitrix24
После получения сообщения от пользователя в боте, бот автоматически сохраняет сообщение и отправляет его в Bitrix24.

5.3. Обработка анкеты
Бот предлагает пользователю анкеты и сохраняет ответы.
Ответы пользователя сохраняются в базе данных и могут быть отправлены в Bitrix24.

6. Примечания
Убедитесь, что все ключи и токены для Bitrix24 и Telegram бота корректны.
В случае проблем с API Bitrix24, проверьте правильность API-ключа и прав доступа.
Вы можете расширить функциональность бота, добавив дополнительные функции для работы с другими модулями Bitrix24.
