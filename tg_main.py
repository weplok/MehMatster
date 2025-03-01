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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
API_TOKEN = '7310603202:AAGC1StqzHRenL-w8ouhneno3G5FRHfl6vM'

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
        [InlineKeyboardButton(text="Общага", callback_data="inf_dorm")],
        [InlineKeyboardButton(text="Кампус", callback_data="inf_campus")]
    ]
)

# Клавиатура для выбора направления (учитель)
direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Математика, механика и математическое моделирование", callback_data="direction_math")],
        [InlineKeyboardButton(text="Прикладная математика и информатика", callback_data="direction_infmath")],
        [InlineKeyboardButton(text="Фундаментальная информатика и информационные технологии, очное обучение", callback_data="direction_inf")],
        [InlineKeyboardButton(text="Педагогическое образование. Профиль «Математика»", callback_data="direction_ped")]
    ]
)

teacher_direction_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Кафедры")],
        [KeyboardButton(text="Бакалавр направление")],
        [KeyboardButton(text="Магистраль направление")],
        [KeyboardButton(text="Аспирантура направление")],
    ],
    resize_keyboard=True
)

choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="choice_yes")],
        [InlineKeyboardButton(text="Нет", callback_data="choice_no")]
    ]
)

# Клавиатура для выбора подкатегорий ПМИ
ivt_subcategory_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Условия", callback_data="ivt_conditions")],
        [InlineKeyboardButton(text="Финансы", callback_data="ivt_finance")],
        [InlineKeyboardButton(text="Инфраструктура", callback_data="ivt_infrastructure")]
    ]
)

# Клавиатура для авторизованного пользователя
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расписание"), KeyboardButton(text="Событие")],
        [KeyboardButton(text="Инфа про препода"), KeyboardButton(text="Навигация")],
        [KeyboardButton(text="Учебные ресурсы")]
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
    if choice == "Расписание":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Сегодня", callback_data="schedule_today")],
            [InlineKeyboardButton(text="Завтра", callback_data="schedule_tomorrow")],
            [InlineKeyboardButton(text="Послезавтра", callback_data="schedule_atomorrow")],
            [InlineKeyboardButton(text="Неделя", callback_data="schedule_week")]
        ])
    elif choice == "Событие":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Последняя новость", callback_data="news_last")],
            [InlineKeyboardButton(text="Ссылка на вк", callback_data="news_vk_url")]
        ])
    return keyboard

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
@dp.message(lambda message: message.text.lower() in ["старт", "начать"])
async def cmd_start(message: types.Message):
    try:
        await message.answer("Добро пожаловать! Выберите вашу роль:", reply_markup=role_keyboard)
    except TelegramAPIError as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

# Обработчик команд /menu, Меню
@dp.message(Command("menu"))
@dp.message(lambda message: message.text.lower() in ["меню", "menu"])
async def cmd_menu(message: types.Message):
    try:
        user_id = message.from_user.id
        user = get_user("tg", user_id)
        if user is None:
            await message.answer("Пожалуйста, завершите регистрацию.")
            return

        if user["is_abitur"] == 1:
            await message.answer("Меню с направлением:", reply_markup=teacher_direction_keyboard)
        else:
            await message.answer("Меню с действиями:", reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Ошибка в обработчике меню: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора роли (студент или абитуриент)
@dp.message(lambda message: message.text in ["Студент", "Абитуриент"])
async def process_role(message: types.Message):
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
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик ввода имени
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_name")
async def process_name(message: types.Message):
    try:
        user_id = message.from_user.id
        user_data[user_id]["name"] = message.text

        if user_data[user_id]["role"] == "abiturient":
            create_user(db_code="tg", uid=user_id, name=message.text, course=None, group=None)
            await message.answer("Регистрация завершена. Вы абитуриент. Вы хотите начать процесс регистрации занова?", reply_markup=choice_keyboard)
            del user_data[user_id]
        elif user_data[user_id]["role"] == "student":
            user_data[user_id]["step"] = "waiting_for_course"
            await message.answer("Выберите ваш курс:", reply_markup=course_keyboard)
    except Exception as e:
        logger.error(f"Ошибка при вводе имени: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора курса (студент)
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_course")
async def process_course(message: types.Message):
    try:
        user_id = message.from_user.id
        user_data[user_id]["course"] = message.text
        user_data[user_id]["step"] = "waiting_for_group"
        await message.answer("Выберите вашу группу:", reply_markup=get_group_keyboard(message.text))
    except Exception as e:
        logger.error(f"Ошибка при выборе курса: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора группы (студент)
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_group")
async def process_group(message: types.Message):
    try:
        user_id = message.from_user.id
        user_data[user_id]["group"] = message.text
        create_user(db_code="tg", uid=user_id, name=user_data[user_id]["name"], course=user_data[user_id]["course"], group=user_data[user_id]["group"])
        await message.answer("Регистрация завершена. Вы студент. Вы хотите начать процесс регистрации занова?", reply_markup=choice_keyboard)
        del user_data[user_id]
    except Exception as e:
        logger.error(f"Ошибка при выборе группы: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик повторной регистрации
@dp.callback_query(lambda callback: callback.data.startswith("choice"))
async def process_re_registration(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        if callback.data == "choice_yes":
            await callback.message.answer("Начнем регистрацию заново. Выберите вашу роль:", reply_markup=role_keyboard)
        elif callback.data == "choice_no":
            user = get_user("tg", user_id)
            if user["is_abitur"] == 1:
                await callback.message.answer("Регистрация отменена. Продолжайте использование бота.", reply_markup=teacher_direction_keyboard)
            else:
                await callback.message.answer("Регистрация отменена. Продолжайте использование бота.", reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Ошибка при повторной регистрации: {e}")
        await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора направления
@dp.callback_query(lambda callback: callback.data.startswith("direction"))
async def process_direction(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        logger.info(f"Пользователь {user_id} выбрал направление: {callback.data}")
        await callback.message.answer(f"Выберите подкатегорию:", reply_markup=ivt_subcategory_keyboard)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при выборе направления: {e}")
        await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора подкатегории ПМИ
@dp.callback_query(lambda callback: callback.data.startswith("ivt_"))
async def process_pmi_subcategory(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        logger.info(f"Пользователь {user_id} выбрал подкатегорию ПМИ: {callback.data}")
        if callback.data == "ivt_conditions":
            await callback.message.answer("Информация об условиях поступления:")
        elif callback.data == "ivt_finance":
            await callback.message.answer("Информация о финансировании...")
        elif callback.data == "ivt_infrastructure":
            await callback.message.answer("Информация об инфраструктуре:", reply_markup=infrastructure_keyboard)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при выборе подкатегории ПМИ: {e}")
        await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора расписания
@dp.callback_query(lambda c: c.data.startswith('schedule_'))
async def process_sch_subchoice(callback_query: types.CallbackQuery):
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
@dp.callback_query(lambda c: c.data.startswith('places_'))
async def process_news_subchoice(callback_query: types.CallbackQuery):
    try:
        subchoice = callback_query.data
        await callback_query.answer()
        if subchoice == "places_paid":
            await callback_query.message.answer("Информация о платных местах...")
        elif subchoice == "places_budget":
            await callback_query.message.answer("Информация о бюджетных местах...")
        elif subchoice == "places_score":
            await callback_query.message.answer("Информация о проходных баллах...")
    except Exception as e:
        logger.error(f"Ошибка при выборе бюджета: {e}")
        await callback_query.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора инфраструктуры
@dp.callback_query(lambda c: c.data.startswith('inf_'))
async def process_news_subchoice(callback_query: types.CallbackQuery):
    try:
        subchoice = callback_query.data
        await callback_query.answer()
        if subchoice == "inf_dorm":
            await callback_query.message.answer("Информация о общаге...")
        elif subchoice == "inf_campus":
            await callback_query.message.answer("Информация о кампусе...")
    except Exception as e:
        logger.error(f"Ошибка при выборе инфраструктуры: {e}")
        await callback_query.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_teacher_fio")
async def process_teacher_fio(message: types.Message):
    try:
        user_id = message.from_user.id
        fio = message.text
        user_data[user_id]["step"] = "waiting_for_teacher_schedule"
        await message.answer(f"Ваш учитель:", reply_markup=get_teacher_keyboard(fio))
    except Exception as e:
        logger.error(f"Ошибка при вводе ФИО учителя: {e}")
        await message.answer("У вашего учителя нет занятий.", reply_markup=ReplyKeyboardRemove)

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_teacher_schedule")
async def process_teacher_schedule(message: types.Message):
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
        await message.answer("У вашего учителя нет занятий.",  reply_markup=ReplyKeyboardRemove())

# Обработчик действий для авторизованного пользователя
@dp.message()
async def handle_actions(message: types.Message):
    try:
        user_id = message.from_user.id
        logger.info(f"Пользователь {user_id} выбрал действие: {message.text}")

        user = get_user("tg", user_id)
        if user is None:
            await message.answer("Пожалуйста, завершите регистрацию.")
            return

        if user["is_abitur"] == 1:
            if message.text == "Кафедры":
                await message.answer("Кафедры...")
            elif message.text == "Бакалавр направление":
                await message.answer("Бакалавр направления", reply_markup=direction_keyboard)
            elif message.text == "Магистраль направление":
                await message.answer("Магистраль направление...")
            elif message.text == "Аспирантура направление":
                await message.answer("Аспирантура направление...")
        else:
            if message.text == "Расписание":
                await message.answer("Выберите период:", reply_markup=get_inline_keyboard(message.text))
            elif message.text == "Событие":
                await message.answer("Выберите новость", reply_markup=get_inline_keyboard(message.text))
            elif message.text == "Инфа про препода":
                await message.answer("Пожалуйста, введите учителя:")
                user_data[user_id] = {"step": "waiting_for_teacher_fio"}
                return
            elif message.text == "Навигация":
                await message.answer("Здесь будет навигация.")
            elif message.text == "Учебные ресурсы":
                await message.answer("Здесь учебные ресурсы.")
            else:
                await message.answer("Используйте кнопки для взаимодействия.")
    except Exception as e:
        logger.error(f"Ошибка в обработчике действий: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())