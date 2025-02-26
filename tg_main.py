'''
Основной файл ТГ-бота.
Если создаете новый файл для ТГ-бота, добавляйте префикс "tg_" в название.
'''

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

# Токен
API_TOKEN = '7362003844:AAFKaYk5S6DFnzyDFOauySExqOHQL29v-z4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Состояния для FSM
class Form(StatesGroup):
    waiting_for_fio = State()
    waiting_for_group = State()
    waiting_for_direction = State()

# Я сюда всю информацию сгружу пользователя
user_data = {}

# Клавиатура для авторизации
auth_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Студент", callback_data="auth_student")],
        [InlineKeyboardButton(text="Учитель", callback_data="auth_teacher")],
        [InlineKeyboardButton(text="Я уже авторизован", callback_data="auth_already")]
    ]
)

# Клавиатура для выбора направления (учитель)
direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ПМИ", callback_data="direction_pmi")],
        [InlineKeyboardButton(text="БИЗНЕС-ИНФА", callback_data="direction_business")]
    ]
)

# Клавиатура для авторизованного пользователя
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расписание"), KeyboardButton(text="Событие")],
        [KeyboardButton(text="Инфа про препода"), KeyboardButton(text="Навигация")],
        [KeyboardButton(text="Учебные ресурсы"), KeyboardButton(text="Сменить роль")]
    ],
    resize_keyboard=True 
)

# Клавиатура для выбора расписания
schedule_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="schedule_today")],
        [InlineKeyboardButton(text="Завтра", callback_data="schedule_tomorrow")],
        [InlineKeyboardButton(text="Неделя", callback_data="schedule_week")]
    ]
)

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Выберите тип авторизации:", reply_markup=auth_keyboard)

# /reser что сбросить авт
@dp.message(Command("reset"))
async def cmd_reset(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    await state.clear() # Очищаем
    await message.answer("Авторизация сброшена. Выберите тип авторизации:", reply_markup=auth_keyboard)

# Обработчик выбора авт
@dp.callback_query()
async def process_auth(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if callback.data == "auth_student":
        await callback.message.answer("Введите ваше ФИО:")
        await state.set_state(Form.waiting_for_fio)
    elif callback.data == "auth_teacher":
        await callback.message.answer("Выберите направление:", reply_markup=direction_keyboard)
        await state.set_state(Form.waiting_for_direction)
    elif callback.data == "auth_already":
        user_data[user_id] = {"auth": True, "user_id": user_id}  # Сохраняем user_id
        await callback.message.answer("Вы авторизованы. Выберите действие:", reply_markup=main_keyboard)

    await callback.answer()

# Обработчик ввода ФИО для студента
@dp.message(Form.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id] = {"auth": True, "role": "student", "fio": message.text, "user_id": user_id}  # Сохраняем юзера

    await message.answer("Теперь введите вашу группу:")
    await state.set_state(Form.waiting_for_group)

# Обработчик ввода группы
@dp.message(Form.waiting_for_group)
async def process_group(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id]["group"] = message.text

    await message.answer(f"Спасибо! Вы авторизованы как студент: {user_data[user_id]['fio']}, группа {user_data[user_id]['group']}.")
    await message.answer("Выберите действие:", reply_markup=main_keyboard)
    await state.clear()

# Обработчик выбора направления для учителя
@dp.callback_query(Form.waiting_for_direction)
async def process_direction(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if callback.data == "direction_pmi":
        user_data[user_id] = {"auth": True, "role": "teacher", "direction": "ПМИ", "user_id": user_id}
    elif callback.data == "direction_business":
        user_data[user_id] = {"auth": True, "role": "teacher", "direction": "БИЗНЕС-ИНФА", "user_id": user_id}

    await callback.message.answer(f"Вы авторизованы как учитель, направление: {user_data[user_id]['direction']}.")
    await callback.message.answer("Выберите действие:", reply_markup=main_keyboard)
    await state.clear()
    await callback.answer()

# Обработчик действий для авт пользователя
@dp.message()
async def handle_actions(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in user_data or not user_data[user_id].get("auth"):
        await message.answer("Сначала авторизуйтесь через /start.")
        return

    if message.text == "Расписание":
        await message.answer("Выберите период:", reply_markup=schedule_keyboard)
    elif message.text == "Событие":
        await message.answer("Здесь будет информация о событиях.")
    elif message.text == "Инфа про препода":
        await message.answer("Здесь будет информация о преподавателе.")
    elif message.text == "Навигация":
        await message.answer("Здесь будет навигация.")
    elif message.text == "Учебные ресурсы":
        await message.answer("Здесь будут учебные ресурсы.")
    elif message.text == "Сменить роль":
        await cmd_reset(message, state)
    else:
        await message.answer("Используйте кнопки для взаимодействия.")

# Обработчик выбора расписания (тут я сво)
@dp.callback_query()
async def process_schedule(callback: types.CallbackQuery):
    if callback.data == "schedule_today":
        await callback.message.answer("Расписание на сегодня: ...") 
    elif callback.data == "schedule_tomorrow":
        await callback.message.answer("Расписание на завтра: ...")
    elif callback.data == "schedule_week":
        await callback.message.answer("Расписание на неделю: ...")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())