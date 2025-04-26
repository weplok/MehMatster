import os
from dotenv import load_dotenv
import requests
import json

# Загрузка переменных окружения и получение API-ключа
load_dotenv()
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY") #В файл .env указать переменную YANDEX_API_KEY

# Проверка наличия API-ключа
if not YANDEX_API_KEY:
    raise ValueError("Необходимо установить переменную окружения YANDEX_API_KEY")


class BotAssistant:  #Создаем класс, который будет хранить историю разговора
    def __init__(self):
        self.history = [] #Инициализируем список для хранения истории

    def ai_ansver(self, text):
        self.history.append("user:" + text) #Добавляем вопрос пользователя в историю

        prompt = {
            "modelUri": "gpt://ИДЕНТИФИКАТОР КЛЮЧА/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": 2000
            },
            "messages": [
                {
                    "role": "system",
                    "text": """Ты - Мехматстер, дружелюбный и энергичный помощник для студентов и абитуриентов Мехмата ЮФУ. Твоя задача - отвечать на вопросы об университете, учебном процессе, поступлении и т.д.  Используй только информацию из предоставленной базы знаний.

    Старайся отвечать простым и понятным языком, как если бы ты разговаривал со своим другом. Избегай бюрократических формулировок.

    Примеры:
    Пользователь: Какие вступительные экзамены нужны на Мехмат?
    Мехматстер: Для поступления на Мехмат ЮФУ тебе понадобятся результаты ЕГЭ по математике, русскому языку и физике (или информатике).

    Пользователь: Где находится деканат?
    Мехматстер: Деканат Мехмата находится в главном корпусе ЮФУ, кабинет 205.

    Если в базе знаний нет информации на вопрос, ответь: К сожалению, я не знаю ответа на этот вопрос. Попробуйте обратиться 
    в деканат или приемную комиссию."""
                },
                {
                    "role": "user",
                    "text": "\n".join(self.history) + '\n---------------\n' + str(text)
                }
            ]
        }  # шаблон запроса для нейросети
        url = 'https://<бакет>.storage.yandexcloud.net/<ключ>' #ИЗМЕНИТЬ
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}" #Используем API-KEY из переменной окружения
        }

        try:
            response = requests.post(url, headers=headers, json=prompt)  # отправка запроса и получение ответа
            response.raise_for_status() # Проверяем, что запрос выполнен успешно (код 200)
            data = response.json()  # Преобразуем JSON-ответ в словарь

            result = data['result']['alternatives'][0]['message']['text']
            self.history.append('system:' + result) #Добавляем ответ в историю
            return result

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к YandexGPT: {e}")
            return "Произошла ошибка при получении ответа от YandexGPT."
        except (KeyError, IndexError) as e:
            print(f"Ошибка при разборе ответа YandexGPT: {e}")
            return "Произошла ошибка при обработке ответа от YandexGPT."
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return "Произошла непредвиденная ошибка."

# ------ Пример использования ------

# Вместо этого используйте класс BotAssistant в своем коде


# Пример использования
if __name__ == '__main__':
    assistant = BotAssistant()
    user_text = "Какие направления подготовки есть на мехмате?"
    response = assistant.ai_ansver(user_text)
    print(response)

    user_text = "А какие проходные баллы?"
    response = assistant.ai_ansver(user_text)
    print(response)


"""def gpt_ans(user_text, user):
    uid = user["id"]
    if uid in users_threads.keys():
        thread = users_threads[uid]
    else:
        thread = client.beta.threads.create()
        users_threads[uid] = thread

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=str(user_text)
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=f"Пользователя зовут {user['name']}. Он - {roles[bool(user['is_abitur'])]}"
    )

    if run.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        return messages.data[0].content[0].text.value
    else:
        return str(run.status)"""
