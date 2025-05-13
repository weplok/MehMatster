# MehMatster
Дружелюбный чат-бот помощник для студентов Мехмата ЮФУ в ТГ и ВК

Пайплайн запуска:

1. Установите завимимости
```bash
pip install -r requirements.txt
```

2. Единожды запустите init_db.py (больше запускать не потребуется)

```bash
cd functions/db/
```

```bash
python init_db.py
```

```bash
cd ../../
```

3. Создайте env файл в папке LLM. Для удобства существует .env.example (переименуйте в .env после редактирования).
OPENAI_KEY можно попросить у t.me/weplok5

4. Запустите Бота. Запуск может длиться несколько минут, так как перед запуском происходит ининциализация нейросети

```bash
python tg_main.py
```

```bash
python vk_main.py

[42_cats_presentation.pptx](https://github.com/user-attachments/files/20189368/42_cats_presentation.pptx)


