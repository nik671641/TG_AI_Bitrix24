from openai import OpenAI
from config import TOKEN_AI
from prompts import SYSTEM_PROMPT

client = OpenAI(api_key=TOKEN_AI)

chat_history = {}


async def ask_gpt(message, data_user):
    user_id = message.from_user.id
    question = message.text

    # получаем данные о пользователе

    # Если истории нет — создаём
    if user_id not in chat_history:
        chat_history[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT + f"Это данные о пользователе для большей коммуникабельности с пользователем {data_user}"}
        ]

    # Добавляем сообщение пользователя в историю
    chat_history[user_id].append({"role": "user", "content": question})

    # Отправляем запрос GPT
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history[user_id],
        temperature=0.7
    )

    answer = completion.choices[0].message.content

    # Добавляем ответ GPT в историю
    chat_history[user_id].append({"role": "assistant", "content": answer})

    # Ограничиваем длину истории (например, 20 сообщений)
    if len(chat_history[user_id]) > 20:
        chat_history[user_id] = chat_history[user_id][-20:]

    return answer
