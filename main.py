import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from bitrix24_API import create_contact_in_bitrix, get_contact_id_by_phone, create_deal_in_bitrix, \
    update_deal_in_bitrix, get_deal_id_by_contact, send_chat_to_bitrix, chat_history
from config import TOKEN_TG, Config
from db.db import DB
from db.storage import UserStorage
from db.storage import Survey, SurveyResponses
from gpt_4 import ask_gpt

# Включаем логирование
logging.basicConfig(level=logging.WARNING)

bot = Bot(token=TOKEN_TG)
dp = Dispatcher()
router = Router()

dp.include_router(router)

# Подключение к базе данных
database = DB(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    login=Config.DB_LOGIN,
    password=Config.DB_PASSWORD,
    database=Config.DB_DATABASE,
)

user_storage = UserStorage(database)
survey_responses = SurveyResponses(database)

# Словарь для хранения переписки {chat_id: [сообщения]}
user_id = None
user_name = None
text = None


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    text = message.text
    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, text)

    reply = await message.answer(
        """Добро пожаловать в Amatto!\n\nМы – компания Amatto, занимаемся продажей стильной и качественной мебели для дома, а также создаем уникальные интерьерные решения в Молдове.\n\nЕсли вы хотите обустроить свое пространство со вкусом или нуждаетесь в профессиональном дизайне интерьера – мы поможем вам найти идеальное решение! """)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Компания", callback_data="category_company")],
        [InlineKeyboardButton(text="👤 Частное лицо", callback_data="category_individual")]
    ])

    reply = await message.answer("Выберите вашу категорию:", reply_markup=keyboard)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)


@router.callback_query(lambda c: c.data.startswith("category_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    category = "Компания" if callback.data == "category_company" else "Частное лицо"
    chat_id = callback.message.chat.id
    user_name = callback.message.from_user
    # Сохраняем ответ пользователя
    await save_message(chat_id, user_name, category)

    if await user_storage.get_by_id(chat_id):
        await user_storage._db.execute(
            "UPDATE users SET category = $1 WHERE user_id = $2", category, callback.from_user.id
        )
    else:
        await user_storage.create(chat_id, callback.from_user.username, callback.from_user.first_name, category)

    reply = await callback.message.answer(
        f"Вы выбрали: {category}\nТеперь давайте перейдем к анкетированию...\nКак вас зовут?")
    # Сохраняем ответ бота
    await save_message(chat_id, "Бот", reply)

    await state.set_state(Survey.name)
    await callback.answer()


@router.message(Survey.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    reply = await message.answer("Спасибо! Теперь введите ваш номер телефона 📞")

    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)
    await state.set_state(Survey.phone)


@router.message(Survey.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    reply = await message.answer("В каком городе вы находитесь?")

    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)

    await state.set_state(Survey.address)


@router.message(Survey.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    reply = await message.answer("Укажите свой email:")

    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)
    await state.set_state(Survey.email)


@router.message(Survey.email)
async def process_private_person(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    user = await user_storage.get_by_id(message.chat.id)
    if user.category == "Частное лицо":
        await state.update_data(category="Частное лицо")

        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Гостиная"), KeyboardButton(text="Спальня")],
            [KeyboardButton(text="Кухня"), KeyboardButton(text="Офисная")],
            [KeyboardButton(text="Другое")]
        ], resize_keyboard=True)

        reply = await message.answer("Какую мебель вы ищете?", reply_markup=keyboard)
        # Сохраняем ответ бота
        await save_message(user_id, "Бот", reply)

        await state.set_state(Survey.furniture_type)
    else:
        await state.update_data(category="Компания")

        reply = await message.answer("Как называется ваша компания?")
        # Сохраняем ответ бота
        await save_message(user_id, "Бот", reply)

        await state.set_state(Survey.company_name)


@router.message(Survey.furniture_type)
async def process_furniture(message: types.Message, state: FSMContext):
    await state.update_data(furniture_type=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ], resize_keyboard=True)

    reply = await message.answer("Интересует ли вас дизайн интерьера?", reply_markup=keyboard)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)
    await state.set_state(Survey.design_interest)


@router.message(Survey.design_interest)
async def process_design(message: types.Message, state: FSMContext):
    await state.update_data(design_interest=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="500€"), KeyboardButton(text="1000€")],
        [KeyboardButton(text="3000€"), KeyboardButton(text="5000€")]
    ], resize_keyboard=True)

    reply = await message.answer("Какой у вас бюджет?", reply_markup=keyboard)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)
    await state.set_state(Survey.budget)


@router.message(Survey.budget)
async def process_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ], resize_keyboard=True)

    reply = await message.answer("Требуется ли доставка и сборка?", reply_markup=keyboard)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)

    await state.set_state(Survey.delivery)


@router.message(Survey.company_name)
async def process_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Разовая покупка"), KeyboardButton(text="На постоянной основе")]
    ], resize_keyboard=True)

    reply = await message.answer("Вы закупаете мебель разово или на постоянной основе?", reply_markup=keyboard)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)

    await state.set_state(Survey.delivery)


@router.message(Survey.delivery)
async def finish_survey(message: types.Message, state: FSMContext):
    await state.update_data(delivery=message.text)

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    data = await state.get_data()
    data["user_id"] = message.from_user.id

    get_user = await survey_responses.get_user_by_id(message.chat.id)
    if not get_user:
        await survey_responses.save_survey(data)
    else:
        await survey_responses.update_survey(message.chat.id, data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Связаться с менеджером", callback_data="contact_manager"),
            InlineKeyboardButton(text="Перейти к оплате", callback_data="go_to_payment"),
            InlineKeyboardButton(text="Дополнительный вопрос", callback_data="extra_question")
        ]
    ])

    reply = await message.answer("Спасибо! Ваши данные отправлены менеджеру. Мы скоро свяжемся с вами! 📞\n"
                                 "Если у вас есть какие-то вопросы смело задавайте))",
                                 reply_markup=keyboard)
    # Сохраняем ответ бота
    await save_message(user_id, "Бот", reply)
    user_crm_id = await get_contact_id_by_phone(data["phone"])

    if not user_crm_id:
        # Если контакт не найден, создаём новый контакт и сделку
        deal_in_bitrix = await create_contact_in_bitrix(data["name"], data["phone"], None, data["address"])
        if deal_in_bitrix:
            # Если контакт успешно создан, создаём сделку
            budget_value = int("".join(filter(str.isdigit, data["budget"])))
            await create_deal_in_bitrix("Сделка с " + data["name"], deal_in_bitrix, budget_value)
    else:
        # Если контакт найден, ищем сделку, связанную с этим контактом
        deal_id_bitrix = await get_deal_id_by_contact(user_crm_id)
        if deal_id_bitrix:
            # Если сделка существует, обновляем её
            await update_deal_in_bitrix("Сделка с " + data["name"], deal_id_bitrix, data["budget"])
        else:
            # Если сделка не найдена, создаём новую сделку
            budget_value = int("".join(filter(str.isdigit, data["budget"])))
            await create_deal_in_bitrix("Сделка с " + data["name"], user_crm_id, budget_value)

    # Обновляем время последней активности
    last_activity[user_id] = datetime.now()

    await state.clear()


@router.callback_query(lambda c: c.data == "contact_manager")
async def contact_manager_callback(callback: types.CallbackQuery):
    await callback.message.answer("Менеджер скоро свяжется с вами!")


@router.callback_query(lambda c: c.data == "go_to_payment")
async def go_to_payment_callback(callback: types.CallbackQuery):
    await callback.message.answer("Перейдите по ссылке для оплаты: https://example.com/payment")


@router.callback_query(lambda c: c.data == "extra_question")
async def extra_question_callback(callback: types.CallbackQuery):
    await callback.message.answer("Какой у вас вопрос?")


@router.message()
async def chat_gpt(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    # Обновляем время последней активности
    last_activity[user_id] = datetime.now()

    # Сохраняем ответ пользователя
    await save_message(user_id, user_name, message.text)

    data_user = await survey_responses.get_by_id(message.chat.id)
    print("data_user", data_user)

    ai_response = await ask_gpt(message, data_user)
    await message.answer(ai_response)

    # Сохраняем ответ бота
    await save_message(user_id, "AI", ai_response)


# Сохраняет сообщение в историю переписки
async def save_message(user_id, user, text):
    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append(f"{user}: {text}")


# Словарь для хранения времени последнего сообщения {user_id: timestamp}
last_activity = {}

# Время ожидания перед авто-сохранением (2 минуты)
AUTO_SAVE_DELAY = 120


async def check_user_activity():
    """Периодически проверяет активность пользователей"""
    user_crm_id = await get_contact_id_by_phone("+37367107269")
    deal_id = await get_deal_id_by_contact(user_crm_id)

    while True:
        now = datetime.now()
        inactive_users = []

        for user_id, last_time in last_activity.items():
            if now - last_time > timedelta(seconds=AUTO_SAVE_DELAY):
                inactive_users.append(user_id)

        for user_id in inactive_users:
            # Отправляем историю в Bitrix24
            if deal_id:
                send_chat_to_bitrix(user_id, deal_id)

            # Очищаем историю после отправки
            if user_id in chat_history:
                chat_history[user_id] = []
                del last_activity[user_id]

            print(f"💾 Автоматически сохранили диалог пользователя {user_id}")

        await asyncio.sleep(60)  # Проверяем раз в минуту


async def main():
    await database.create_pool()

    try:
        await user_storage.init()
        await survey_responses.init()
        asyncio.create_task(check_user_activity())
        await dp.start_polling(bot, skip_updates=False)
    finally:
        await database.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
