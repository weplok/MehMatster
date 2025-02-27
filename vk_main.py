'''
Основной файл ВК-бота.
Если создаете новый файл для ВК-бота, добавляйте префикс "vk_" в название.
'''

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from functions.db_funcs import *

# Инициализация сессии
vk_session = vk_api.VkApi(token='vk1.a.aGFNn-rcVNqmHl_jtBbqXJMFHfDpp29wJzjvsk307yJ4a4eLD6zmVF8c01XjsJuwggDpF6-OGK6FV82zcXXFLyyA8I0jksu_D3A1WzmrMFU-CUP740rjOO85tI29z9SoeL861nRSsh5TxEMIci4GhAxHi3XuRP6q5vkPdXgAW75JhDMrwyro7DVtGWTNSPPWmSFMW5U8GCGTLeSXX0MS-w')  # Замените на ваш токен
vk = vk_session.get_api()

# Инициализация LongPoll
group_id = 229563001  # Замените на ID вашего сообщества
longpoll = VkBotLongPoll(vk_session, group_id)

# Функция для создания клавиатуры
def create_keyboard(buttons, inline=False):
    keyboard = VkKeyboard(one_time=False, inline=inline)
    for button in buttons:
        keyboard.add_button(button, color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()

# Функция для отправки сообщения
def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard
    )


# Основной цикл бота
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        text = event.obj.message['text']
        keyboard = create_keyboard(['Начать'], inline=False)

        if text.lower() == 'начать':
            # Убираем кнопку "Начать" и показываем новые кнопки
            """if get_user("vk", user_id):
                # Предлагаем выбор: Расписание, События, Информация о преподавателях, Навигация, Учебные ресурсы
                keyboard = create_keyboard(
                    ['Расписание', 'События', 'Информация о преподавателях', 'Навигация', 'Учебные ресурсы'],
                    inline=False)
                send_message(user_id, 'Выберите раздел:', keyboard)"""
            """else:
                keyboard = create_keyboard(['Студент', 'Абитуриент', 'начать'], inline=False)
                send_message(user_id, 'Вы студент или абитуриент?', keyboard)"""

        elif text == 'Студент':
            # Запрашиваем данные студента
            send_message(user_id, 'Пожалуйста, введите ваши данные в формате: ФИО, группа, курс.')

        elif text == 'Абитуриент':
            # Предлагаем выбор: Условие, Финансы, Инфраструктура
            keyboard = create_keyboard(['Условие', 'Финансы', 'Инфраструктура', 'начать'], inline=False)
            send_message(user_id, 'Выберите интересующий вас раздел:', keyboard)

        elif text == 'Финансы':
            # Предлагаем выбор: Бюджет, Платное
            keyboard = create_keyboard(['Бюджет', 'Платное', 'начать'], inline=False)
            send_message(user_id, 'Выберите тип обучения:', keyboard)

        elif text == 'Бюджет':
            # Сообщение для выбора "Бюджет"
            send_message(user_id, 'Вы выбрали "Бюджет". Обучение на бюджетной основе.')

        elif text == 'Платное':
            # Сообщение для выбора "Платное"
            send_message(user_id, 'Вы выбрали "Платное". Обучение на платной основе.')

        elif text == 'Инфраструктура':
            # Предлагаем выбор: Общага, Кампус
            keyboard = create_keyboard(['Общага', 'Кампус', 'начать'], inline=False)
            send_message(user_id, 'Выберите тип проживания:', keyboard)

        elif text == 'Общага':
            # Сообщение для выбора "Общага"
            send_message(user_id, 'Вы выбрали "Общага". Проживание в общежитии.')

        elif text == 'Кампус':
            # Сообщение для выбора "Кампус"
            send_message(user_id, 'Вы выбрали "Кампус". Проживание в кампусе.')

        elif text == 'Условие':
            # Сообщение для выбора "Условие"
            send_message(user_id, 'Здесь будет информация об условиях поступления.')

        elif text == 'Уже авторизован':
            # Предлагаем выбор: Расписание, События, Информация о преподавателях, Навигация, Учебные ресурсы
            keyboard = create_keyboard(['Расписание', 'События', 'Информация о преподавателях', 'Навигация', 'Учебные ресурсы', 'начать'], inline=False)
            send_message(user_id, 'Выберите раздел:', keyboard)

        elif text == 'Расписание':
            # Предлагаем выбор: Сегодня, Завтра, Неделя
            keyboard = create_keyboard(['начать''Сегодня', 'Завтра', 'Неделя'], inline=False)
            send_message(user_id, 'Выберите период:', keyboard)

        elif text == 'Сегодня':
            # Сообщение для выбора "Сегодня"
            send_message(user_id, 'Ваше расписание на сегодня: ...')

        elif text == 'Завтра':
            # Сообщение для выбора "Завтра"
            send_message(user_id, 'Ваше расписание на завтра: ...')

        elif text == 'Неделя':
            # Сообщение для выбора "Неделя"
            send_message(user_id, 'Ваше расписание на неделю: ...')

        elif text == 'События':
            # Предлагаем выбор: Последние новости, Ссылка на ТГ
            keyboard = create_keyboard(['Последние новости', 'Ссылка на ТГ', 'начать'], inline=False)
            send_message(user_id, 'Выберите действие:', keyboard)

        elif text == 'Последние новости':
            # Сообщение для выбора "Последние новости"
            send_message(user_id, 'Последние новости: ...')

        elif text == 'Информация о преподавателях':
            # Сообщение для выбора "Информация о преподавателях"
            send_message(user_id, 'Информация о преподавателях: ...')

        elif text == 'Навигация':
            # Сообщение для выбора "Навигация"
            send_message(user_id, 'Навигация по кампусу: ...')

        elif text == 'Учебные ресурсы':
            # Сообщение для выбора "Учебные ресурсы"
            send_message(user_id, 'Учебные ресурсы: ...')

        else:
            # Обработка введенных данных студента
            if ',' in text:
                data = text.split(',')
                if len(data) == 3:
                    fio, group, course = data
                    send_message(user_id, f'Спасибо! Ваши данные: ФИО - {fio}, группа - {group}, курс - {course}.')
                else:
                    send_message(user_id, 'Пожалуйста, введите данные в правильном формате: ФИО, группа, курс.')
            else:
                send_message(user_id, 'Я не понимаю вас. Напишите "начать", чтобы начать.')