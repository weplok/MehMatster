import asyncio
import logging
import pprint
from functions.db_funcs import create_user, get_user
from functions.schedule import get_groups, get_schedule
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
API_TOKEN = '7362003844:AAFKaYk5S6DFnzyDFOauySExqOHQL29v-z4'

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

# Клавиатура для бюджета
budget_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Бюджет", callback_data="places_paid")],
        [InlineKeyboardButton(text="Платка", callback_data="places_budget")]
    ]
)

# Клавиатура для выбора направления (учитель)
direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ПМИ", callback_data="direction_pmi")],
        [InlineKeyboardButton(text="ИВТ", callback_data="direction_ivt")]
    ]
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
    # Заглушка для функции get_groups
    # Возвращает клавиатуру с группами для выбранного курса
    groups = get_groups(course)  # Пример групп
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=group)] for group in groups],
        resize_keyboard=True
    )
    return keyboard

# Обработчик команд /start, Старт, Начать
@dp.message(Command("start"))
@dp.message(lambda message: message.text.lower() in ["старт", "начать"])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Выберите вашу роль:", reply_markup=role_keyboard)

# Обработчик команд /start, Старт, Начать
@dp.message(Command("menu"))
@dp.message(lambda message: message.text.lower() in ["меню", "menu"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if get_user("tg", user_id)["is_abitur"] == 1:
            await message.answer("Меню с направлением:", reply_markup=direction_keyboard)
    else:
        await message.answer("Меню с действиями:", reply_markup=main_keyboard)

# Обработчик выбора роли (студент или абитуриент)
@dp.message(lambda message: message.text in ["Студент", "Абитуриент"])
async def process_role(message: types.Message):
    user_id = message.from_user.id
    role = message.text.lower()
    if role == "студент":
        await message.answer("Введите ваше имя:", reply_markup=ReplyKeyboardRemove())  # Убираем клавиатуру
        user_data[user_id] = {"role": "student", "step": "waiting_for_name"}
    elif role == "абитуриент":
        await message.answer("Введите ваше имя:", reply_markup=ReplyKeyboardRemove())  # Убираем клавиатуру
        user_data[user_id] = {"role": "abiturient", "step": "waiting_for_name"}

# Обработчик ввода имени
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("step") == "waiting_for_name")
async def process_name(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text

    if user_data[user_id]["role"] == "abiturient":
        # Для абитуриента регистрация завершена
        create_user(db_code="tg", uid=user_id, name=message.text, course=None, group=None)
        await message.answer("Регистрация завершена. Вы аббитурент. Вы хотите начать процесс регистарции занова?", reply_markup=choice_keyboard)
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
    create_user(db_code="tg", uid=user_id, name=user_data[user_id]["name"], course=user_data[user_id]["course"], group=user_data[user_id]["group"])

    await message.answer("Регистрация завершена. Вы студент. Вы хотите начать процесс регистарции занова?", reply_markup=choice_keyboard)
    del user_data[user_id]  # Очищаем временные данные

# Обработчик повторной регистрации
@dp.callback_query(lambda callback: callback.data.startswith("choice"))
async def process_re_registration(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "choice_yes":
        await callback.message.answer("Начнем регистрацию заново. Выберите вашу роль:", reply_markup=role_keyboard)
    elif callback.data == "choice_no":
        if get_user("tg", user_id)["is_abitur"] == 1:
            await callback.message.answer("Регистрация отменена. Продолжайте использование бота.", reply_markup=direction_keyboard)
        else:
            await callback.message.answer("Регистрация отменена. Продолжа-йте использование бота.", reply_markup=main_keyboard)

# Обработчик выбора направления (для учителя)
@dp.callback_query(lambda callback: callback.data.startswith("direction"))
async def process_direction(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал направление: {callback.data}")

    if callback.data == "direction_ivt":
        user_data[user_id] = {"auth": True, "role": "teacher", "direction": "ПМИ", "user_id": user_id}
        await callback.message.answer("Выберите подкатегорию ИВТ:", reply_markup=ivt_subcategory_keyboard)
    elif callback.data == "direction_mpi":
        user_data[user_id] = {"auth": True, "role": "teacher", "direction": "БИЗНЕС-ИНФА", "user_id": user_id}
        await callback.message.answer("Бла бла бла")

    await callback.answer()

# Обработчик выбора подкатегории ПМИ
@dp.callback_query(lambda callback: callback.data.startswith("ivt_"))
async def process_pmi_subcategory(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал подкатегорию ПМИ: {callback.data}")

    if callback.data == "ivt_conditions":
        await callback.message.answer("Информация об условиях поступления:")
    elif callback.data == "ivt_finance":
        await callback.message.answer("Информация о финансировании:", reply_markup=budget_keyboard)
    elif callback.data == "ivt_infrastructure":
        await callback.message.answer("Информация об инфраструктуре:", reply_markup=infrastructure_keyboard)

    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith('schedule_'))
async def process_sch_subchoice(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    person = get_user("tg", user_id)
    subchoice = callback_query.data
    await callback_query.answer()
    if subchoice == "schedule_today":
        await callback_query.message.answer(f"{pprint.pformat(get_schedule(person["course"], person["group"], "today"))}")
    elif subchoice == "schedule_tomorrow":
        await callback_query.message.answer(f"{pprint.pformat(get_schedule(person["course"], person["group"], "tomorrow"))}")
    elif subchoice == "schedule_week":
        await callback_query.message.answer(f"{pprint.pformat(get_schedule(person["course"], person["group"], "week"))}")
    elif subchoice == "schedule_atomorrow":
        await callback_query.message.answer(f"{pprint.pformat(get_schedule(person["course"], person["group"], "atomorrow"))}")

@dp.callback_query(lambda c: c.data.startswith('places_'))
async def process_news_subchoice(callback_query: types.CallbackQuery):
    subchoice = callback_query.data
    await callback_query.answer()
    if subchoice == "places_paid":
        await callback_query.message.answer("Информация о платных местах...")
    elif subchoice == "places_budget":
        await callback_query.message.answer("Информация о бюджетных местах...")

@dp.callback_query(lambda c: c.data.startswith('inf_'))
async def process_news_subchoice(callback_query: types.CallbackQuery):
    subchoice = callback_query.data
    await callback_query.answer()
    if subchoice == "inf_dorm":
        await callback_query.message.answer("Информация о общаге...")
    elif subchoice == "inf_campus":
        await callback_query.message.answer("Информация о кампусе...")

# Обработчик действий для авторизованного пользователя
@dp.message()
async def handle_actions(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} выбрал действие: {message.text}")

    if message.text == "Расписание":
        await message.answer("Выберите период:", reply_markup=get_inline_keyboard(message.text))
    elif message.text == "Событие":
        await message.answer("Выбертите новость", reply_markup=get_inline_keyboard(message.text))
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