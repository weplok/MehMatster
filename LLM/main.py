import requests
import argparse

URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


def run(iam_token, folder_id, user_text):
    # Собираем запрос
    data = {}
    # Указываем тип модели
    data["modelUri"] = f"gpt://{folder_id}/yandexgpt"
    # Настраиваем опции
    data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}
    # Указываем контекст для модели
    data["messages"] = [
        {"role": "system", "text": "Твоя установка: Ты - помощник на основе имеющихся у тебя данных. Отвечай так, чтобы соответствовать тому, что тебе дано заранее. Твои данные, которые необходимо использовать: Резиновые уточки - посланники сатаны."},
        {"role": "user", "text": f"{user_text}"},
    ]

    # Отправляем запрос
    response = requests.post(
        URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Api-Key {iam_token}"
        },
        json=data,
    ).json()

    # Распечатываем результат
    print(response)


if __name__ == '__main__':
    api_key = "AQVN33DOKM5m3eR9prsoE7tmZaNNfG0Agb88OrU0"
    folder_id= "b1g1hrqgd7lvvch2499s"
    user_text = "Что ты думаешь насчет пластмассовых уточек?"
    run(api_key, folder_id, user_text)
