import requests
from config import BITRIX24_API_KEY, BITRIX24_DOMAIN


chat_history = {}
# Создание клиента
async def create_contact_in_bitrix(name, phone, email, address):
    url = f"{BITRIX24_DOMAIN}/rest/1/{BITRIX24_API_KEY}/crm.contact.add.json"

    params = {
        "fields": {
            "NAME": name,
            "PHONE": [{"VALUE": str(phone), "VALUE_TYPE": "WORK"}],  # Преобразуем в строку
            "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}],
            "ADDRESS": address
        }
    }

    response = requests.post(url, json=params)  # Передаём JSON
    data = response.json()

    if "result" in data:
        print(f"Контакт создан! ID: {data['result']}")
        return data["result"]  # Возвращаем ID контакта

    print(f"Ошибка: {data}")  # Вывод ошибки, если что-то пошло не так
    return None


# create_contact_in_bitrix("Иван", +37367234567, "narzullozugurov88@gmail.com", "Кишинев")


# Функция для создания сделки в Bitrix24
async def create_deal_in_bitrix(title, contact_id, opportunity):
    url = f"{BITRIX24_DOMAIN}/rest/1/{BITRIX24_API_KEY}/crm.deal.add.json"

    params = {
        "fields": {
            "TITLE": title,
            "CONTACT_ID": contact_id,  # Привязка к контакту
            "OPPORTUNITY": opportunity,  # Сумма сделки
            "STAGE_ID": "NEW",  # Этап сделки (например, новый клиент)
            "CURRENCY_ID": "USD"  # Валюта
        }
    }

    response = requests.post(url, json=params)  # Отправляем JSON
    deal = response.json()

    if "result" in deal:
        print(f"Сделка создана! ID: {deal['result']}")
        return deal["result"]

    print(f"Ошибка: {deal}")
    return None


# обновление сделки
async def update_deal_in_bitrix(deal_id, new_title=None, new_opportunity=None, new_stage=None):
    url = f"{BITRIX24_DOMAIN}/rest/1/{BITRIX24_API_KEY}/crm.deal.update.json"

    fields = {}

    if new_title:
        fields["TITLE"] = new_title
    if new_opportunity:
        fields["OPPORTUNITY"] = new_opportunity
    if new_stage:
        fields["STAGE_ID"] = new_stage

    if not fields:
        print("Нет данных для обновления.")
        return None

    params = {
        "id": deal_id,  # ID сделки, которую обновляем
        "fields": fields
    }

    response = requests.post(url, json=params)  # Отправляем JSON
    result = response.json()

    if "result" in result and result["result"] == True:
        print(f"Сделка {deal_id} успешно обновлена!")
        return True

    print(f"Ошибка обновления: {result}")
    return False


# поиск id контакта по телефону
async def get_contact_id_by_phone(phone):
    phone = phone.replace(" ", "")  # Убираем пробелы, если есть

    url = f"{BITRIX24_DOMAIN}/rest/1/{BITRIX24_API_KEY}/crm.contact.list.json"

    params = {
        "filter[PHONE]": phone,  # Используем правильный синтаксис для фильтрации
        "select": ["ID"]
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "result" in data and data["result"]:
        return data["result"][0]["ID"]  # Возвращаем ID первого найденного контакта
    return None


# # Пример поиска контакта с номером телефона в нужном формате
# phone_number = "+37367107269"
# contact_id = get_contact_id_by_phone(phone_number)
# print(f"ID клиента с номером {phone_number}: {contact_id}")

# Получить id контракта по contact_id
async def get_deal_id_by_contact(contact_id):
    url = f"{BITRIX24_DOMAIN}/rest/1/{BITRIX24_API_KEY}/crm.deal.list.json"

    # Параметры для фильтрации сделок по контакту
    params = {
        "filter[CONTACT_ID]": contact_id,  # Фильтрация по ID контакта
        "select": ["ID"]  # Указываем, что хотим получить только ID сделок
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Если результат есть, возвращаем ID первой сделки
    if "result" in data and data["result"]:
        return data["result"][0]["ID"]  # Возвращаем ID первой найденной сделки
    return None


# Функция для сохранения переписки
def send_chat_to_bitrix(user_id, deal_id):
    """Отправляет всю переписку в Bitrix24"""
    if user_id in chat_history and chat_history[user_id]:
        full_chat = "\n".join(chat_history[user_id])  # Собираем переписку

        url = f"{BITRIX24_DOMAIN}/rest/1/{BITRIX24_API_KEY}/crm.timeline.comment.add.json"
        params = {
            "fields": {
                "ENTITY_ID": deal_id,
                "ENTITY_TYPE": "deal",
                "COMMENT": full_chat
            }
        }

        response = requests.post(url, json=params)
        data = response.json()

        if "result" in data:
            chat_history[user_id] = []  # Очищаем историю после отправки
            return True
    return False
