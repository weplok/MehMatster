from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
API_TOKEN = '7362003844:AAFKaYk5S6DFnzyDFOauySExqOHQL29v-z4'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатура для меню
def get_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Действие 1")],
            [KeyboardButton(text="Действие 2")],
            [KeyboardButton(text="Действие 3")]
        ],
        resize_keyboard=True  # Клавиатура подстраивается под размер экрана
    )
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот с меню. Введите /menu, чтобы открыть меню.")

# Обработчик команды /menu
@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer("", reply_markup=get_menu_keyboard())  # Пустое сообщение с клавиатурой

# Обработчик выбора действия
@dp.message(lambda message: message.text in ["Действие 1", "Действие 2", "Действие 3"])
async def process_action(message: types.Message):
    if message.text == "Действие 1":
        await message.answer("Вы выбрали Действие 1!")
    elif message.text == "Действие 2":
        await message.answer("Вы выбрали Действие 2!")
    elif message.text == "Действие 3":
        await message.answer("Вы выбрали Действие 3!")

# Обработчик всех остальных сообщений
@dp.message()
async def handle_other_messages(message: types.Message):
    await message.answer("Используйте команду /menu, чтобы открыть меню.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())