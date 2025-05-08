import asyncio
import logging
import pprint
import ast
from functions.db_funcs import create_user, get_user
from functions.schedule import get_groups, get_schedule, get_teachers, get_teacher_schedule
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.exceptions import TelegramAPIError
from config import API_TOKEN
from parsing import base_info_master, base_info_bachalor, student_get_news, student_get_news_mehmat
# from LLM.gpt_funcs import gpt_ans
import datetime


# База данных для хранения информации о пользователях и времени запросов (в памяти)
user_request_times = {}
REQUEST_LIMIT = 5  # Максимальное количество запросов
TIME_WINDOW = 20 # В секундах

student_news = student_get_news()
student_mehmath_news = student_get_news_mehmat()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранение данных пользователя (временное, вместо БД)
user_data = {}

# Клавиатура для выбора роли (студент или абитуриент)
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Студент")],
        [KeyboardButton(text="Абитуриент")]
    ],
    resize_keyboard=True
)

#клавиатура с преподавателями
teacher_info_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Конкретный преподаватель")],
        [KeyboardButton(text="Общая информация о преподавателях")]
    ],
    resize_keyboard=True
)


# Клавиатура для выбора курса (студент)
course_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Бакалавриат, 1 курс")],
        [KeyboardButton(text="Бакалавриат, 2 курс")],
        [KeyboardButton(text="Бакалавриат, 3 курс")],
        [KeyboardButton(text="Бакалавриат, 4 курс")],
        [KeyboardButton(text="Бакалавриат, 5 курс")],
        [KeyboardButton(text="Магистратура, 1 курс")],
        [KeyboardButton(text="Магистратура, 2 курс")],
        [KeyboardButton(text="Аспирантура, 1 курс")],
        [KeyboardButton(text="Аспирантура, 2 курс")]
    ],
    resize_keyboard=True
)

# Клавиатура для бюджета
infrastructure_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Общага на ул. Зорге 21", callback_data="nav_21")],
        [InlineKeyboardButton(text="Общага на ул. Зорге 28", callback_data="nav_28")],
        [InlineKeyboardButton(text="Кампус", callback_data="nav_campus")]
    ]
)

keyboard_labels = {
    "direction_math": "Математика и механика",
    "direction_infmath": "Прикладная математика и информатика",
    "direction_inf": "Фундаментальная информатика и информационные технологии",
    "direction_ped": "Педагогическое образование: Математика",
}

keyboard_labels_master = {
    "master_fiit": "Фундаментальная математика, механика и математическое моделирование",
    "master_cm": "Computational modeling in technology and finance",
    "master_msd": "Modern software development",
    "master_rmp": "Разработка мобильных приложений и компьютерных игр",
    "master_ii": "Искусственный интеллект: математические модели и прикладные решения",
    "master_mitou": "Модели и информационные технологии организационного управления",
    "master_irpi": "Математика и информатика в образовании",
    "master_mio": "Модели и информационные технологии организационного управления",

}

# Клавиатура для выбора направления (учитель)
direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=keyboard_labels["direction_math"], callback_data="direction_math")],
        [InlineKeyboardButton(text=keyboard_labels["direction_infmath"], callback_data="direction_infmath")],
        [InlineKeyboardButton(text=keyboard_labels["direction_inf"], callback_data="direction_inf")],
        [InlineKeyboardButton(text=keyboard_labels["direction_ped"], callback_data="direction_ped")]
    ]
)

#магистратура кнопки программ
master_keyboard_dir = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=keyboard_labels_master['master_fiit'], callback_data='master_fiit')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_cm'], callback_data='master_cm')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_msd'], callback_data='master_msd')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_rmp'], callback_data='master_rmp')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_ii'], callback_data='master_ii')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_mitou'], callback_data='master_mitou')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_irpi'], callback_data='master_irpi')],
        [InlineKeyboardButton(text=keyboard_labels_master['master_mio'], callback_data='master_mio')]
    ]
)

teacher_direction_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Кафедры")],
        [KeyboardButton(text="Бакалавриат направления")],
        [KeyboardButton(text="Магистратура направления")],
        [KeyboardButton(text="Аспирантура направления")],
        [KeyboardButton(text="В начало <-")],
    ],
    resize_keyboard=True
)

choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="choice_yes")],
        [InlineKeyboardButton(text="Нет", callback_data="choice_no")]
    ]
)



# # Клавиатура для выбора подкатегорий ПМИ
# ivt_subcategory_keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="Финансы", callback_data="ivt_finance")],
#         [InlineKeyboardButton(text="Инфраструктура", callback_data="ivt_infrastructure")]
#     ]
# )

# Клавиатура для авторизованного пользователя
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мое расписание 📆"), KeyboardButton(text="События 🎭")],
        [KeyboardButton(text="Информация о преподавателях 👩‍🏫"), KeyboardButton(text="Навигация 🌏")],
        [KeyboardButton(text="В начало <-")],
    ],
    resize_keyboard=True
)

# Функция для форматирования расписания
def format_schedule(schedule):
    days_dict = {
        "0": "Понедельник",
        "1": "Вторник",
        "2": "Среда",
        "3": "Четверг",
        "4": "Пятница",
        "5": "Суббота",
        "6": "Воскресенье",
    }
    result = []
    for day, lessons in schedule.items():
        result.append(f"📅 День недели: {days_dict[day]}")
        for lesson in lessons:
            result.append(
                f"  🕒 Время: {lesson['start_time']} - {lesson['end_time']}\n"
                f"  📚 Предмет: {lesson['title']}\n"
                f"  🏫 Аудитория: {lesson['room']}\n"
                f"  👩‍🏫 Преподаватель: {lesson['teacher']}\n"
            )
        result.append("")  # Пустая строка для разделения дней
    return "\n".join(result)

# Клавиатура для выбора расписания
def get_inline_keyboard(choice: str):
    if choice == "Мое расписание 📆":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Сегодня", callback_data="schedule_today")],
            [InlineKeyboardButton(text="Завтра", callback_data="schedule_tomorrow")],
            [InlineKeyboardButton(text="Послезавтра", callback_data="schedule_atomorrow")],
            [InlineKeyboardButton(text="Неделя", callback_data="schedule_week")]
        ])
    elif choice == "События 🎭":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Последние новости ЮФУ", callback_data="news_last")],
            [InlineKeyboardButton(text="Последние новости Мехмата", callback_data="news_last_mehmath")],
            [InlineKeyboardButton(text="Пресс-Центр ЮФУ", callback_data="news_url")]
        ])

    return keyboard


@dp.callback_query(lambda c: c.data.startswith('news_'))
async def process_news_subchoice(callback_query: types.CallbackQuery):
    if await anti_spam(callback_query.message):  # Добавляем проверку
        return  # Прекращаем обработку, если спам
    subchoice = callback_query.data
    await callback_query.answer()
    if subchoice == "news_last":
        await callback_query.message.answer("Последние новости ЮФУ:")
        await callback_query.message.answer(student_news)
    if subchoice == "news_last_mehmath":
        await callback_query.message.answer("Последние новости Мехмата:")
        await callback_query.message.answer(student_mehmath_news)
    elif subchoice == "news_url":
        await callback_query.message.answer("Больше новостей:")
        await callback_query.message.answer('<a href="https://sfedu.ru/press-center/newspage/1">''😽👉тык👈''</a>',parse_mode="HTML")



# Клавиатура для выбора группы (студент)
def get_group_keyboard(course):
    try:
        groups = get_groups(course)  # Пример групп
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=group)] for group in groups],
            resize_keyboard=True
        )
        return keyboard
    except Exception as e:
        logger.error(f"Ошибка при получении групп: {e}")
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)

# Клавиатура для выбора преподавателя
def get_teacher_keyboard(name):
    try:
        teachers = get_teachers(name)  # Пример преподавателей
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=teacher)] for teacher in teachers],
            resize_keyboard=True
        )
        return keyboard
    except Exception as e:
        logger.error(f"Ошибка при получении преподавателей: {e}")
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)

# Обработчик команд /start, Старт, Начать
@dp.message(Command("start"))
@dp.message(lambda message: message.text.lower() in ["старт", "начать", "в начало <-"])
async def cmd_start(message: types.Message):
    if await anti_spam(message):
        return
    try:
        await bot.send_sticker(message.from_user.id, sticker='CAACAgIAAxkBAAEN7PRnw5QEfyJq8OiXvkgYCUAYK_g-QgACEmMAAvlZAUpPtMZ1_L5TTzYE')
        await message.answer("Добро пожаловать!\nМеня зовут кот-МехМатстер 😸\nЯ помогу вам с поступлением или учебой в нашем прекрасном университете ЮФУ города Ростова-на-Дону 🌃\n\nДля начала работы выберите роль:", reply_markup=role_keyboard)
    except TelegramAPIError as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

# @dp.message(Command("?"))
# @dp.message(lambda message: message.text.lower() in ["?", "вопросы"])
# async def cmd_start(message: types.Message):
#     if await anti_spam(message):
#        return
#     try:
#         await message.answer("Задайте свой вопрос?")
#         user_message = message.text
#         user_id = message.from_user.id
#         user_data[user_id]= {"step": "waiting_for_quest"}
#
#     except TelegramAPIError as e:
#         logger.error(f"Ошибка при отправке сообщения: {e}")
#         await message.answer("Задайте вопрос еще раз.")
#
# @dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_quest")
# async def process_name(message: types.Message):
#     if await anti_spam(message):
#        return
#     user_id = message.from_user.id
#     quest = message.text
#     await bot.send_sticker(user_id, sticker='CAACAgIAAxkBAAEN7PZnw5QSHc42ibnJokgy3QFClBcKZgACBGUAAsZRGEoi2-q_Kk1_lzYE')
#     await message.answer(gpt_ans(quest, get_user("tg", user_id)))


# Обработчик команд /menu, Меню
@dp.message(Command("menu"))
@dp.message(lambda message: message.text.lower() in ["меню", "menu"])
async def cmd_menu(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        user = get_user("tg", user_id)
        if user is None:
            await message.answer("Пожалуйста, завершите регистрацию")
            return

        if user["is_abitur"] == 1:
            await message.answer("Меню с направлением:", reply_markup=teacher_direction_keyboard)
        else:
            await message.answer("Меню с действиями:", reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Ошибка в обработчике меню: {e}")
        await message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже")

# Обработчик выбора роли (студент или абитуриент)
@dp.message(lambda message: message.text in ["Студент", "Абитуриент"])
async def process_role(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        role = message.text.lower()
        if role == "студент":
            await message.answer("Введите ваше имя:", reply_markup=ReplyKeyboardRemove())
            user_data[user_id] = {"role": "student", "step": "waiting_for_name"}
        elif role == "абитуриент":
            await message.answer("Введите ваше имя:", reply_markup=ReplyKeyboardRemove())
            user_data[user_id] = {"role": "abiturient", "step": "waiting_for_name"}
    except Exception as e:
        logger.error(f"Ошибка при выборе роли: {e}")
        await message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже.")

# Обработчик ввода имени
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_name")
async def process_name(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        user_data[user_id]["name"] = message.text

        if user_data[user_id]["role"] == "abiturient":
            create_user(db_code="tg", uid=user_id, name=message.text, course=None, group=None)
            await message.answer("Поздравляю! 🐱\nРегистрация завершена. \nВы абитуриент 🧑‍💼 \n\nХотите начать процесс регистрации заново?", reply_markup=choice_keyboard)
            del user_data[user_id]
        elif user_data[user_id]["role"] == "student":
            user_data[user_id]["step"] = "waiting_for_course"
            await message.answer("Выберите ваш курс:", reply_markup=course_keyboard)
    except Exception as e:
        logger.error(f"Ошибка при вводе имени: {e}")
        await message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже")

# Обработчик выбора курса (студент)
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_course")
async def process_course(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        user_data[user_id]["course"] = message.text
        user_data[user_id]["step"] = "waiting_for_group"
        await message.answer("Выберите вашу группу:", reply_markup=get_group_keyboard(message.text))
    except Exception as e:
        logger.error(f"Ошибка при выборе курса: {e}")
        await message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже.")

# Обработчик выбора группы (студент)
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_group")
async def process_group(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        user_data[user_id]["group"] = message.text
        create_user(db_code="tg", uid=user_id, name=user_data[user_id]["name"], course=user_data[user_id]["course"], group=user_data[user_id]["group"])
        await message.answer("Поздравляю! 🐱\nРегистрация завершена. \nВы студент 👨‍🎓 \n\nХотите начать процесс регистрации заново?", reply_markup=choice_keyboard)
        del user_data[user_id]
    except Exception as e:
        logger.error(f"Ошибка при выборе группы: {e}")
        await message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже.")

@dp.callback_query(lambda callback: callback.data.startswith("nav_"))
async def process_direction(callback: types.CallbackQuery):
    if await anti_spam(callback.message):
        return
    try:
        images = ["https://imgur.com/a/oanUdfd.png", "https://imgur.com/a/nUi4hmJ.png",
                  "https://imgur.com/a/jYFm862.png", "https://imgur.com/a/1410HTN.png",
                  "https://imgur.com/a/RmMmlFt.png"]
        if callback.data == "nav_21":
            await callback.message.answer("https://imgur.com/a/oanUdfd.png")
            await callback.message.answer("https://imgur.com/a/nUi4hmJ.png")
        elif callback.data == "nav_28":
            await callback.message.answer("https://imgur.com/a/jYFm862.png")
        elif callback.data == "nav_campus":
            await callback.message.answer("https://imgur.com/a/1410HTN.png")
            await callback.message.answer("https://imgur.com/a/RmMmlFt.png")

    except Exception as e:
        logger.error(f"Ошибка при выборе направления: {e}")
        await callback.message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже.")

# Обработчик повторной регистрации
@dp.callback_query(lambda callback: callback.data.startswith("choice"))
async def process_re_registration(callback: types.CallbackQuery):
    if await anti_spam(callback.message):
        return
    try:
        user_id = callback.from_user.id
        if callback.data == "choice_yes":
            await callback.message.answer("Начнем регистрацию заново. Выберите вашу роль:", reply_markup=role_keyboard)
        elif callback.data == "choice_no":
            user = get_user("tg", user_id)
            if user["is_abitur"] == 1:
                await callback.message.answer("Регистрация отменена. Можете продолжить использование бота 🐈", reply_markup=teacher_direction_keyboard)
            else:
                await callback.message.answer("Регистрация отменена. Можете продолжить использование бота 🐈", reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Ошибка при повторной регистрации: {e}")
        await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора направления бакалавриата
@dp.callback_query(lambda callback: callback.data.startswith("direction"))
async def process_direction(callback: types.CallbackQuery):
    if await anti_spam(callback.message):
        return
    try:
        user_id = callback.from_user.id
        label = keyboard_labels[callback.data]
        logger.info(f"Пользователь {user_id} выбрал направление: {label}")
        await bot.send_sticker(user_id, sticker='CAACAgIAAxkBAAEN7PZnw5QSHc42ibnJokgy3QFClBcKZgACBGUAAsZRGEoi2-q_Kk1_lzYE')

        await callback.message.answer(base_info_bachalor(label))

    except Exception as e:
        logger.error(f"Ошибка при выборе направления: {e}")
        await callback.message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже.")



@dp.callback_query(lambda callback: callback.data.startswith("master"))
async def process_master(callback: types.CallbackQuery):
    if await anti_spam(callback.message):
        return
    try:
        user_id = callback.from_user.id
        label = keyboard_labels_master[callback.data]
        logger.info(f"Пользователь {user_id} выбрал направление: {label}")
        await bot.send_sticker(user_id, sticker='CAACAgIAAxkBAAEN7PZnw5QSHc42ibnJokgy3QFClBcKZgACBGUAAsZRGEoi2-q_Kk1_lzYE')
        await callback.message.answer(base_info_master(label))
    except Exception as e:
        logger.error(f"Ошибка при выборе направления: {e}")
        await callback.message.answer("Произошла ошибка⛔ Пожалуйста, попробуйте позже.")

# # Обработчик выбора подкатегории ПМИ
# @dp.callback_query(lambda callback: callback.data.startswith("ivt_"))
# async def process_pmi_subcategory(callback: types.CallbackQuery):
#     try:
#         user_id = callback.from_user.id
#         logger.info(f"Пользователь {user_id} выбрал подкатегорию ПМИ: {callback.data}")
#         if callback.data == "ivt_finance":
#             await callback.message.answer("Информация о финансировании...")
#         elif callback.data == "ivt_infrastructure":
#             await callback.message.answer("Информация об инфраструктуре:", reply_markup=infrastructure_keyboard)
#         await callback.answer()
#     except Exception as e:
#         logger.error(f"Ошибка при выборе подкатегории ПМИ: {e}")
#         await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора расписания
@dp.callback_query(lambda c: c.data.startswith('schedule_'))
async def process_sch_subchoice(callback_query: types.CallbackQuery):
    if await anti_spam(callback_query.message):
        return
    try:
        user_id = callback_query.from_user.id
        person = get_user("tg", user_id)
        subchoice = callback_query.data
        await callback_query.answer()
        if subchoice == "schedule_today":
            schedule_text = f"{get_schedule(person['course'], person['group'], 'today')}"
            start_index = schedule_text.find("{")
            end_index = schedule_text.rfind("}") + 1
            schedule_data = ast.literal_eval(schedule_text[start_index:end_index])
            await callback_query.message.answer(f"{format_schedule(schedule_data)}")
        elif subchoice == "schedule_tomorrow":
            schedule_text = f"{get_schedule(person['course'], person['group'], 'tomorrow')}"
            start_index = schedule_text.find("{")
            end_index = schedule_text.rfind("}") + 1
            schedule_data = ast.literal_eval(schedule_text[start_index:end_index])
            await callback_query.message.answer(f"{format_schedule(schedule_data)}")
        elif subchoice == "schedule_week":
            schedule_text = f"{get_schedule(person['course'], person['group'], 'week')}"
            start_index = schedule_text.find("{")
            end_index = schedule_text.rfind("}") + 1
            schedule_data = ast.literal_eval(schedule_text[start_index:end_index])
            await callback_query.message.answer(f"{format_schedule(schedule_data)}")
        elif subchoice == "schedule_atomorrow":
            schedule_text = f"{get_schedule(person['course'], person['group'], 'atomorrow')}"
            start_index = schedule_text.find("{")
            end_index = schedule_text.rfind("}") + 1
            schedule_data = ast.literal_eval(schedule_text[start_index:end_index])
            await callback_query.message.answer(f"{format_schedule(schedule_data)}")
    except Exception as e:
        logger.error(f"Ошибка при выборе расписания: {e}")
        await callback_query.message.answer("Выходной")

# Обработчик выбора бюджета
# @dp.callback_query(lambda c: c.data.startswith('places_'))
# async def process_news_subchoice(callback_query: types.CallbackQuery):
#     try:
#         subchoice = callback_query.data
#         await callback_query.answer()
#         if subchoice == "places_paid":
#             await callback_query.message.answer("Информация о платных местах...")
#         elif subchoice == "places_budget":
#             await callback_query.message.answer("Информация о бюджетных местах...")
#         elif subchoice == "places_score":
#             await callback_query.message.answer("Информация о проходных баллах...")
#     except Exception as e:
#         logger.error(f"Ошибка при выборе бюджета: {e}")
#         await callback_query.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# # Обработчик выбора инфраструктуры
# @dp.callback_query(lambda c: c.data.startswith('inf_'))
# async def process_news_subchoice(callback_query: types.CallbackQuery):
#     try:
#         subchoice = callback_query.data
#         await callback_query.answer()
#         if subchoice == "inf_dorm":
#             await callback_query.message.answer("Информация о общаге...")
#         elif subchoice == "inf_campus":
#             await callback_query.message.answer("Информация о кампусе...")
#     except Exception as e:
#         logger.error(f"Ошибка при выборе инфраструктуры: {e}")
#         await callback_query.message.answer("Произошла ошибка ⛔ Пожалуйста, попробуйте позже.")

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_teacher_fio")
async def process_teacher_fio(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        fio = message.text
        user_data[user_id]["step"] = "waiting_for_teacher_schedule"
        await message.answer(f"Ваш учитель:", reply_markup=get_teacher_keyboard(fio))
    except Exception as e:
        logger.error(f"Ошибка при вводе ФИО учителя: {e}")
        await message.answer("У вашего учителя нет занятий", reply_markup=ReplyKeyboardRemove)

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_teacher_schedule")
async def process_teacher_schedule(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        fio = message.text
        user_data[user_id]["step"] = None

        schedule_text = f"{get_teacher_schedule(fio, 'week')}"
        start_index = schedule_text.find("{")
        end_index = schedule_text.rfind("}") + 1

        schedule_data = ast.literal_eval(schedule_text[start_index:end_index])
        await message.answer(f"Расписание учителя:")
        if format_schedule(schedule_data):
            await message.answer(f"{format_schedule(schedule_data)}", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Ошибка при получении расписания учителя: {e}")
        await message.answer("У вашего учителя нет занятий",  reply_markup=ReplyKeyboardRemove())

# Обработчик действий для авторизованного пользователя
@dp.message()
async def handle_actions(message: types.Message):
    if await anti_spam(message):
        return
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        logger.info(f"Пользователь {user_id} выбрал действие: {message.text}")

        user = get_user("tg", user_id)
        if user is None:
            await message.answer("Пожалуйста, завершите регистрацию")
            return

        if user["is_abitur"] == 1:
            if message.text == "Кафедры":
                await bot.send_sticker(user_id, sticker='CAACAgIAAxkBAAEN7PZnw5QSHc42ibnJokgy3QFClBcKZgACBGUAAsZRGEoi2-q_Kk1_lzYE')
                await message.answer('Тут вообще должна ответить нейросеть, но у разрабов нет денег, чтобы ее оплатить) Скиньте 1500 пж')
            elif message.text == "Бакалавриат направления":
                await message.answer("Бакалавриат направления", reply_markup=direction_keyboard)
            elif message.text == "Магистратура направления":
                await message.answer("Магистратура направления", reply_markup=master_keyboard_dir)
            elif message.text == "Аспирантура направления":
                await message.answer("Математика и механика \n\n Математическое моделирование, численные методы и комплексы программ. Математические модели естественных наук "
                                     "\n\n Управление в организационных системах \n\n Математическое и программное обеспечение вычислительных систем, комплексов и компьютерных сетей")
        else:
            if message.text == "Мое расписание 📆":
                await message.answer("Выберите период:", reply_markup=get_inline_keyboard(message.text))
            elif message.text == "События 🎭":
                await message.answer("Какие новости вас интересуют? 🐱📸", reply_markup=get_inline_keyboard(message.text))
            elif message.text == "Информация о преподавателях 👩‍🏫":
                await message.answer("Пожалуйста, выберите опцию:", reply_markup=teacher_info_keyboard)
            elif message.text == "Навигация 🌏":
                await message.answer("Выберите навигацию:", reply_markup=infrastructure_keyboard)

            else:
                await message.answer("Используйте кнопки для взаимодействия.")
    except Exception as e:
        logger.error(f"Ошибка в обработчике действий: {e}")
        await message.answer("Произошла ошибка ⛔ Пожалуйста, попробуйте позже.")

# Обработчик для кнопки "Конкретный преподаватель"
@dp.message_handler(lambda message: message.text == "Конкретный преподаватель")
async def enter_teacher_name(message: types.Message):
    if await anti_spam(message):
        return
    user_id = message.from_user.id
    await message.answer("Пожалуйста, введите имя учителя:")
    user_data[user_id] = {"step": "waiting_for_teacher_fio"}
    return

# Обработчик для кнопки "Общая информация о преподавателях"
@dp.message_handler(lambda message: message.text == "Общая информация о преподавателях")
async def provide_teacher_info(message: types.Message):
    if await anti_spam(message):
        return
    # Создаем клавиатуру с гиперссылкой
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Сайт вуза", url="https://sfedu.ru/www/stat_pages22.show?p=ELs/sotr/D&x=ELS/2000000000000")
    keyboard.add(button)

    await message.answer(
        "Для получения дополнительной информации вы можете посетить сайт вуза:",
        reply_markup=keyboard
    )

async def anti_spam(message: types.Message) -> bool:
    user_id = message.from_user.id
    current_time = datetime.datetime.now()

    if user_id in user_request_times:
        requests = user_request_times[user_id]
        requests = [time for time in requests if (current_time - time).total_seconds() <= TIME_WINDOW]
        if len(requests) >= REQUEST_LIMIT:
            await message.reply(
                "Пожалуйста, не отправляйте запросы так часто. Попробуйте через {} секунд.".format(
                    TIME_WINDOW - int((current_time - requests[0]).total_seconds())
                )
            )
            return True  # Прекращаем обработку
        requests.append(current_time)
        user_request_times[user_id] = requests
    else:
        user_request_times[user_id] = [current_time]
    return False  # Продолжаем обработку
    
# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
