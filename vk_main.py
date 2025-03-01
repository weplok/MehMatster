from sys import flags

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from MehMatster.functions.db_funcs import get_user
from MehMatster.functions.schedule import get_schedule, get_groups
from functions import db_funcs.get_user()
from functions import schedule.get_schedule()
from functions import schedule.get_groups()

user_states = {}

# Инициализация сессии
vk_session = vk_api.VkApi(token='vk1.a.aGFNn-rcVNqmHl_jtBbqXJMFHfDpp29wJzjvsk307yJ4a4eLD6zmVF8c01XjsJuwggDpF6-OGK6FV82zcXXFLyyA8I0jksu_D3A1WzmrMFU-CUP740rjOO85tI29z9SoeL861nRSsh5TxEMIci4GhAxHi3XuRP6q5vkPdXgAW75JhDMrwyro7DVtGWTNSPPWmSFMW5U8GCGTLeSXX0MS-w')  # Замените на ваш токен
vk = vk_session.get_api()

# Инициализация LongPoll
group_id = 229563001  # Замените на ID вашего сообщества
longpoll = VkBotLongPoll(vk_session, group_id)

# Функция для создания клавиатуры
def create_keyboard(buttons, inline=False, one_time=False):
    keyboard = vk_api.keyboard.VkKeyboard(one_time=one_time, inline=inline)
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

def show_menu(user_id):
    keyboard = create_keyboard(['Расписание', 'События', 'Информация о преподавателях', 'Навигация', 'Учебные ресурсы'])
    send_message(user_id, 'Menu', keyboard)

def schedule(user_id):
    # Отправляем клавиатуру с выбором расписания
    keyboard = create_keyboard(['Сегодня', 'Завтра', 'Послезавтра', 'Неделя', 'Меню'])
    send_message(user_id, 'Выберите период:', keyboard)

    # Обработка выбора периода
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']

            if text == 'Сегодня':
                send_message(user_id, 'Ваше расписание на сегодня: ...')
                break  # Выходим из цикла после обработки

            elif text == 'Завтра':
                send_message(user_id, 'Ваше расписание на завтра: ...')
                break

            elif text == 'Послезавтра':
                send_message(user_id, 'Ваше расписание на послезавтра: ...')
                break

            elif text == 'Неделя':
                send_message(user_id, 'Ваше расписание на неделю: ...')
                break

            elif text.lower() == '/menu' or text.lower() == 'menu' or text.lower() == 'меню':
                show_menu(user_id)

            else:
                send_message(user_id, 'Пожалуйста, выберите период из предложенных вариантов.')

# Основной цикл бота
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        text = event.obj.message['text']
        flags_noregister = None
        flags_register = None

        if text.lower() == '/start' or text.lower() == 'start':
            # Отправляем сообщение с кнопкой "Начать" (одноразовая клавиатура)
            if get_user("vk", user_id):
                # Предлагаем выбор: Расписание, События, Информация о преподавателях, Навигация, Учебные ресурсы
                keyboard = create_keyboard(
                    ['Да', 'Нет'],
                    inline=False)
                send_message(user_id, 'Вы хотите пройти процесс регистрации заново?', keyboard)
            else:
                keyboard = create_keyboard(['Студент', 'Абитуриент'], one_time=True)
                send_message(user_id, 'Вы студент или абитуриент?', keyboard)

        elif text == 'Да':
            # После нажатия на "Начать" клавиатура пропадает
            keyboard = create_keyboard(['Студент', 'Абитуриент'], one_time=True)
            send_message(user_id, 'Вы Студент или Абитуриент?', keyboard)

        elif text == 'Нет':
            # После нажатия на "Начать" клавиатура пропадает
            show_menu(user_id)


        elif text == 'Студент':
            user_states[user_id] = {'step': 'ask_name', 'role': 'student'}  # Устанавливаем состояние "ask_name" и роль "student"
            send_message(user_id, 'Пожалуйста, введите ваше имя:')

        elif text == 'Абитуриент':
            user_states[user_id] = {'step': 'ask_name', 'role': 'applicant'}  # Устанавливаем состояние "ask_name" и роль "applicant"
            send_message(user_id, 'Пожалуйста, введите ваше имя:')


        elif user_states[user_id].get('step') == 'ask_name' and user_states[user_id].get('role') == 'student':
            user_states[user_id]['name'] = text  # Сохраняем имя
            user_states[user_id]['step'] = 'ask_group'  # Переходим к следующему шагу
            send_message(user_id, 'Теперь введите вашу группу:')
            # Обработка ввода группы для студента

        elif user_states[user_id].get('step') == 'ask_group' and user_states[user_id].get('role') == 'student':
            user_states[user_id]['group'] = text  # Сохраняем группу
            user_states[user_id]['step'] = 'ask_course'  # Переходим к следующему шагу
            send_message(user_id, 'Теперь введите ваш курс:')
            # Обработка ввода курса для студента

        elif user_states[user_id].get('step') == 'ask_course' and user_states[user_id].get('role') == 'student':
            user_states[user_id]['course'] = text  # Сохраняем курс
          # Выводим все данные
            name = user_states[user_id]['name']
            group = user_states[user_id]['group']
            course = user_states[user_id]['course']
            send_message(user_id, f'Спасибо! Ваши данные: Имя - {name}, группа - {group}, курс - {course}.')
            # Сбрасываем состояние пользователя
            user_states[user_id] = {}
            # Обработка ввода имени для абитуриента

        elif user_states[user_id].get('step') == 'ask_name' and user_states[user_id].get('role') == 'applicant':
            user_states[user_id]['name'] = text  # Сохраняем имя
            # Выводим данные
            name = user_states[user_id]['name']
            send_message(user_id, f'Спасибо! Ваше имя: {name}.')
            # Сбрасываем состояние пользователя
            user_states[user_id] = {}

        elif text == 'Финансы':
            # Предлагаем выбор: Бюджет, Платное
            keyboard = create_keyboard(['Бюджет', 'Платное'])
            send_message(user_id, 'Выберите тип обучения:', keyboard)

        elif text == 'Бюджет':
            # Сообщение для выбора "Бюджет"
            send_message(user_id, 'Вы выбрали "Бюджет". Обучение на бюджетной основе.')

        elif text == 'Платное':
            # Сообщение для выбора "Платное"
            send_message(user_id, 'Вы выбрали "Платное". Обучение на платной основе.')

        elif text == 'Инфраструктура':
            # Предлагаем выбор: Общага, Кампус
            keyboard = create_keyboard(['Общага', 'Кампус'])
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
            keyboard = create_keyboard(['Расписание', 'События', 'Информация о преподавателях', 'Навигация', 'Учебные ресурсы'])
            send_message(user_id, 'Выберите раздел:', keyboard)

        elif text == 'Расписание':
            # Предлагаем выбор: Сегодня, Завтра, Неделя
            schedule(user_id)

        elif text == 'События':
            # Предлагаем выбор: Последние новости, Ссылка на ТГ
            keyboard = create_keyboard(['Последние новости', 'Ссылка на ТГ'])
            send_message(user_id, 'Выберите действие:', keyboard)

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
