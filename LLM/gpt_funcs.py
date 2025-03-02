import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(
    api_key=OPENAI_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, 'data', "knowledge_base.txt")
file = client.files.create(
    file=open(file_path, "rb"),
    purpose="assistants"
)

vector_file = client.beta.vector_stores.create(
    name="vector_store",
    file_ids=[file.id]
)

assistant = client.beta.assistants.create(
    name="Мехматстер - Дружелюбный помощник Мехмата ЮФУ",
    instructions="Роль – дружелюбный и энергичный помощник для студентов и абитуриентов университета ЮФУ. Задача – отвечать на вопросы студентов и абитуриентов, которые есть в данной базе знаний. Главное – выражаться не бюрократически, а на ровне, как человек к человеку.",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_file.id]
        }
    },
    model="gpt-4o-mini"
)
assistant_id = assistant.id

roles = {
    False: "Студент",
    True: "Абитуриент"
}


def gpt_ans(user_text, user):
    thread = client.beta.threads.create()

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
        return str(run.status)


print(gpt_ans("Где находится Мехмат?", {'name': "Максим", "is_abitur": True}))
