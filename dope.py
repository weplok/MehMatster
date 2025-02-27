from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import asyncio

# Вставьте сюда ваш токен
API_TOKEN = '7362003844:AAFKaYk5S6DFnzyDFOauySExqOHQL29v-z4'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбор 1", callback_data="choice1")],
        [InlineKeyboardButton(text="Выбор 2", callback_data="choice2")],
        [InlineKeyboardButton(text="Выбор 3", callback_data="choice3")]
    ])
    await message.answer("Пожалуйста, выберите:", reply_markup=keyboard)

# Обработчик Inline-кнопок
@dp.callback_query(lambda c: c.data.startswith('choice'))
async def process_callback_choice(callback_query: types.CallbackQuery):
    choice = callback_query.data

    if choice == 'choice1':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подвыбор 1.1", callback_data="subchoice1_1")],
            [InlineKeyboardButton(text="Подвыбор 1.2", callback_data="subchoice1_2")]
        ])
        await callback_query.message.edit_text("Вы выбрали Выбор 1. Теперь выберите подвыбор:", reply_markup=keyboard)
    elif choice == 'choice2':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подвыбор 2.1", callback_data="subchoice2_1")],
            [InlineKeyboardButton(text="Подвыбор 2.2", callback_data="subchoice2_2")]
        ])
        await callback_query.message.edit_text("Вы выбрали Выбор 2. Теперь выберите подвыбор:", reply_markup=keyboard)
    elif choice == 'choice3':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подвыбор 3.1", callback_data="subchoice3_1")],
            [InlineKeyboardButton(text="Подвыбор 3.2", callback_data="subchoice3_2")]
        ])
        await callback_query.message.edit_text("Вы выбрали Выбор 3. Теперь выберите подвыбор:", reply_markup=keyboard)

# Обработчик подвыборов
@dp.callback_query(lambda c: c.data.startswith('subchoice'))
async def process_callback_subchoice(callback_query: types.CallbackQuery):
    subchoice = callback_query.data
    await callback_query.answer()

    # Убираем кнопки, передавая reply_markup=None
    await callback_query.message.edit_text(f"Вы выбрали: {subchoice}", reply_markup=None)

# Запуск бота
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))