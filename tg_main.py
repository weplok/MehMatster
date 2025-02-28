from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging
from parsing import student_get_news, applicant_count_free_places, applicant_count_paid_places, student_get_news_mehmat

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
API_TOKEN = '7310603202:AAGC1StqzHRenL-w8ouhneno3G5FRHfl6vM'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

student_news = student_get_news()
student_news_mehmath = student_get_news_mehmat()
# applicant_c_paid_places = applicant_count_paid_places()
# applicant_c_free_places = applicant_count_free_places()


# Моковые функции для работы с БД
def get_user(code, user_id):
    # Заглушка для функции get_user
    # Возвращает пустой словарь, если пользователя нет, и словарь с данными, если он есть
    return {}

def create_user(code, user_id, name, course=None, group=None, is_abitur=None):
    # Заглушка для функции create_user
    # Создает пользователя в БД
    logger.info(f"Создан пользователь: id={user_id}, name={name}, course={course}, group={group}")

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
budget_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="БЮДЖЕТ", callback_data="direction_pmi")],
        [InlineKeyboardButton(text="ПЛАТКА", callback_data="direction_business")]
    ]
)

# Клавиатура для выбора направления (учитель)
direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ПМИ", callback_data="direction_pmi")],
        [InlineKeyboardButton(text="БИЗНЕС-ИНФА", callback_data="direction_business")]
    ]
)


# Клавиатура для выбора подкатегорий ПМИ
pmi_subcategory_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Условия", callback_data="pmi_conditions")],
        [InlineKeyboardButton(text="Финансы", callback_data="pmi_finance")],
        [InlineKeyboardButton(text="Инфраструктура", callback_data="pmi_infrastructure")]
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

# Клавиатура для выбора расписания

def get_inline_keyboard(choice: str):
    if choice == "Расписание":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Сегодня", callback_data="schedule_today")],
            [InlineKeyboardButton(text="Завтра", callback_data="schedule_tomorrow")],
            [InlineKeyboardButton(text="Неделя", callback_data="schedule_week")]
        ])
    elif choice == "Событие":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Последние новости ЮФУ", callback_data="news_last")],
            [InlineKeyboardButton(text="Последние новости Мехмата", callback_data="news_last_mehmath")],
            [InlineKeyboardButton(text="Пресс-Центр ЮФУ", callback_data="news_vk_url")]
        ])
    return keyboard


# Клавиатура для выбора группы (студент)
def get_group_keyboard(course):
    # Заглушка для функции get_groups
    # Возвращает клавиатуру с группами для выбранного курса
    groups = ["Группа 1", "Группа 2", "Группа 3"]  # Пример групп
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=group)] for group in groups],
        resize_keyboard=True
    )
    return keyboard


# Обработчик команд /start, Старт, Начать
@dp.message(Command("start"))
@dp.message(lambda message: message.text.lower() in ["старт", "начать"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = get_user("tg", user_id)  # Проверяем, авторизован ли пользователь



    if user:
        # Если пользователь уже авторизован, спрашиваем, хочет ли он пройти регистрацию заново
        await message.answer("Вы уже авторизованы. Хотите пройти регистрацию заново?", reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Да")],
                [KeyboardButton(text="Нет")]
            ],
            resize_keyboard=True
        ))
    else:
        # Если пользователь не авторизован, начинаем регистрацию
        await message.answer("Добро пожаловать! Выберите вашу роль:", reply_markup=role_keyboard)

# Обработчик выбора роли (студент или абитуриент)
@dp.message(lambda message: message.text in ["Студент", "Абитуриент"])
async def process_role(message: types.Message):
    user_id = message.from_user.id
    role = message.text.lower()

    if role == "студент":
        await message.answer("Введите ваше имя:")
        user_data[user_id] = {"role": "student", "step": "waiting_for_name"}
    elif role == "абитуриент":
        await message.answer("Введите ваше имя:")
        user_data[user_id] = {"role": "abiturient", "step": "waiting_for_name"}

# Обработчик ввода имени
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_name")
async def process_name(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text

    if user_data[user_id]["role"] == "abiturient":
        # Для абитуриента регистрация завершена
        create_user("tg", user_id, message.text, is_abitur=True)
        await message.answer("Регистрация завершена. Вы зашли как абитуриент.", reply_markup=direction_keyboard)
        del user_data[user_id]  # Очищаем временные данные
    else:
        # Для студента запрашиваем курс
        user_data[user_id]["step"] = "waiting_for_course"
        await message.answer("Выберите ваш курс:", reply_markup=course_keyboard)

# Обработчик выбора курса (студент)
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_course")
async def process_course(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["course"] = message.text
    user_data[user_id]["step"] = "waiting_for_group"
    await message.answer("Выберите вашу группу:", reply_markup=get_group_keyboard(message.text))

# Обработчик выбора группы (студент)
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_group")
async def process_group(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["group"] = message.text

    # Завершаем регистрацию студента
    create_user("tg", user_id, user_data[user_id]["name"], user_data[user_id]["course"], user_data[user_id]["group"])
    await message.answer("Регистрация завершена. Вы зашли как студент.", reply_markup=main_keyboard)
    del user_data[user_id]  # Очищаем временные данные

# Обработчик повторной регистрации
@dp.message(lambda message: message.text.lower() in ["да", "нет"])
async def process_re_registration(message: types.Message):
    user_id = message.from_user.id
    if message.text.lower() == "да":
        await message.answer("Начнем регистрацию заново. Выберите вашу роль:", reply_markup=role_keyboard)
    else:
        await message.answer("Регистрация отменена. Продолжайте использование бота.")


# Обработчик выбора направления (для учителя)
@dp.callback_query(lambda callback: callback.data.startswith("direction"))
async def process_direction(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал направление: {callback.data}")

    if callback.data == "direction_pmi":
        user_data[user_id] = {"auth": True, "role": "teacher", "direction": "ПМИ", "user_id": user_id}
        await callback.message.answer("Выберите подкатегорию ПМИ:", reply_markup=pmi_subcategory_keyboard)
    elif callback.data == "direction_business":
        user_data[user_id] = {"auth": True, "role": "teacher", "direction": "БИЗНЕС-ИНФА", "user_id": user_id}
        await callback.message.answer(f"Вы авторизованы как учитель, направление: {user_data[user_id]['direction']}.")
        await callback.message.answer("Выберите действие:", reply_markup=main_keyboard)

    await callback.answer()

# Обработчик выбора подкатегории ПМИ
@dp.callback_query(lambda callback: callback.data.startswith("pmi_"))
async def process_pmi_subcategory(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал подкатегорию ПМИ: {callback.data}")

    if callback.data == "pmi_conditions":
        await callback.message.answer("Информация об условиях поступления на ПМИ: ...")
    elif callback.data == "pmi_finance":
        await callback.message.answer("Информация о финансировании на ПМИ: ...")
    elif callback.data == "pmi_infrastructure":
        await callback.message.answer("Информация об инфраструктуре на ПМИ: ...")

    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith('schedule_'))
async def process_sch_subchoice(callback_query: types.CallbackQuery):
    subchoice = callback_query.data
    await callback_query.answer()
    if subchoice == "schedule_today":
        await callback_query.message.answer("Расписание на сегодня")
    elif subchoice == "schedule_tomorrow":
        await callback_query.message.answer("Расписание на завтра")
    elif subchoice == "schedule_week":
        await callback_query.message.answer("Расписание на неделю")


@dp.callback_query(lambda c: c.data.startswith('news_'))
async def process_news_subchoice(callback_query: types.CallbackQuery):
    subchoice = callback_query.data
    await callback_query.answer()
    if subchoice == "news_last":
        await callback_query.message.answer("Последние новости ЮФУ:")
        await callback_query.message.answer(student_news)
    if subchoice == "news_last_mehmath":
        await callback_query.message.answer("Последние новости Мехмата:")
        await callback_query.message.answer(student_news_mehmath)
    elif subchoice == "news_vk_url":
        await callback_query.message.answer("Больше новостей:")
        await callback_query.message.answer('<a href="https://sfedu.ru/press-center/newspage/1">''😽👉тык👈''</a>',parse_mode="HTML")

# Обработчик действий для авторизованного пользователя
@dp.message()
async def handle_actions(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} выбрал действие: {message.text}")

    if message.text == "Расписание":
        await message.answer("Выберите период:", reply_markup=get_inline_keyboard(message.text))
    elif message.text == "Событие":
        await message.answer("Какие новости вы хотите знать", reply_markup=get_inline_keyboard(message.text))
    elif message.text == "Инфа про препода":
        await message.answer("Здесь будет информация о преподавателе.")
    elif message.text == "Навигация":
        await message.answer("Здесь будет навигация.")
    elif message.text == "Учебные ресурсы":
        await message.answer("Здесь учебные ресурсы.")
    else:
        await message.answer("Используйте кнопки для взаимодействия.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())