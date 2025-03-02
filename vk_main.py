from sys import flags
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from parsing import student_get_news, student_get_news_mehmat
from functions import db_funcs, schedule
from functions.db_funcs import get_user, create_user
from functions.schedule import get_groups, get_schedule, get_teachers, get_teacher_schedule
import ast

user_states = {}


def format_schedule(schedule):
    result = []
    days_dict = {
        "0": "Понедельник",
        "1": "Вторник",
        "2": "Среда",
        "3": "Четверг",
        "4": "Пятница",
        "5": "Суббота",
        "6": "Воскресенье",
    }
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


# Инициализация сессии
vk_session = vk_api.VkApi(
    token='vk1.a.aGFNn-rcVNqmHl_jtBbqXJMFHfDpp29wJzjvsk307yJ4a4eLD6zmVF8c01XjsJuwggDpF6-OGK6FV82zcXXFLyyA8I0jksu_D3A1WzmrMFU-CUP740rjOO85tI29z9SoeL861nRSsh5TxEMIci4GhAxHi3XuRP6q5vkPdXgAW75JhDMrwyro7DVtGWTNSPPWmSFMW5U8GCGTLeSXX0MS-w')  # Замените на ваш токен
vk = vk_session.get_api()

# Инициализация LongPoll
group_id = 229563001  # Замените на ID вашего сообщества
longpoll = VkBotLongPoll(vk_session, group_id)


# Функция для создания клавиатуры
def create_keyboard(buttons, inline=False, one_time=False):
    keyboard = vk_api.keyboard.VkKeyboard(one_time=one_time, inline=inline)
    # Добавляем кнопки, разбивая их на строки
    for i, button in enumerate(buttons):
        if i % 2 == 0 and i != 0:  # После каждых 4 кнопок начинаем новую строку
            keyboard.add_line()
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


def register(user_id, text):
    # Проверяем, есть ли пользователь в словаре состояний
    if user_id not in user_states:
        user_states[user_id] = {}

    # Обработка начального выбора роли (студент или абитуриент)
    if text == 'Студент':
        user_states[user_id] = {'step': 'ask_name', 'role': 'student'}
        send_message(user_id, 'Пожалуйста, введите ваше имя:')

    elif text == 'Абитуриент':
        user_states[user_id] = {'step': 'ask_name', 'role': 'applicant'}
        send_message(user_id, 'Пожалуйста, введите ваше имя:')

    # Обработка ввода имени для студента
    elif user_states[user_id].get('step') == 'ask_name' and user_states[user_id].get('role') == 'student':
        user_states[user_id]['name'] = text
        user_states[user_id]['step'] = 'ask_course'  # Переходим к вводу курса

        # Создаем клавиатуру для выбора курса
        keyboard = create_keyboard([
            "Бакалавриат, 1 курс", "Бакалавриат, 2 курс", "Бакалавриат, 3 курс",
            "Бакалавриат, 4 курс", "Бакалавриат, 5 курс", "Магистратура, 1 курс",
            "Магистратура, 2 курс", "Аспирантура, 1 курс", "Аспирантура, 2 курс"
        ])
        send_message(user_id, 'Теперь выберите вашу группу:', keyboard)

    # Обработка ввода курса для студента
    elif user_states[user_id].get('step') == 'ask_course' and user_states[user_id].get('role') == 'student':
        user_states[user_id]['course'] = text
        user_states[user_id]['step'] = 'ask_group'  # Переходим к вводу группы
        group_course = get_groups(text)  # Используем функцию get_groups для получения групп
        if group_course:
            keyboard = create_keyboard(group_course)
            send_message(user_id, 'Теперь выберите вашу группу:', keyboard)
        else:
            send_message(user_id, 'Группы для выбранного курса не найдены.')
            user_states[user_id] = {}  # Сбрасываем состояние

        # Создаем клавиатуру для выбора группы

    # Обработка ввода группы для студента
    elif user_states[user_id].get('step') == 'ask_group' and user_states[user_id].get('role') == 'student':
        user_states[user_id]['group'] = text
        name = user_states[user_id]['name']
        course = user_states[user_id]['course']
        group = user_states[user_id]['group']
        send_message(user_id, f'Спасибо! Ваши данные: Имя - {name}, курс - {course}, группа - {group}.')

        # Сохраняем данные в базу данных
        create_user("vk", user_id, name, course, group)

        # Сбрасываем состояние и показываем меню для студента
        user_states[user_id] = {}
        show_menu_student(user_id)

    # Обработка ввода имени для абитуриента
    elif user_states[user_id].get('step') == 'ask_name' and user_states[user_id].get('role') == 'applicant':
        user_states[user_id]['name'] = text
        name = user_states[user_id]['name']
        send_message(user_id, f'Спасибо! Ваше имя: {name}.')

        # Сохраняем данные в базу данных
        create_user("vk", user_id, name)

        # Сбрасываем состояние и показываем меню для абитуриента
        user_states[user_id] = {}
        show_menu_applicant(user_id)

    # Обработка неожиданного ввода
    else:
        send_message(user_id, 'Пожалуйста, следуйте инструкциям.')


def show_menu_student(user_id):
    keyboard = create_keyboard(['Расписание', 'События', 'Информация о преподавателях', 'Навигация'], one_time=True)
    send_message(user_id, 'Меню для студентов:', keyboard)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']

            if text == "Расписание":
                schedule_vk_bot(user_id)

            elif text == "Информация о преподавателях":
                teachher_schedule_vk_bot(user_id)

            elif text == "События":
                ivent(user_id)


def show_menu_applicant(user_id):
    keyboard = create_keyboard(['Условия поступления', 'Финансы', 'Инфраструктура'], one_time=True)
    send_message(user_id, 'Меню для абитуриентов:', keyboard)

def show_menu_teacher(user_id):
    keyboard = create_keyboard(['Расписание', 'Информация о студентах', 'Навигация', 'Учебные ресурсы'], one_time=True)
    send_message(user_id, 'Меню для преподавателей:', keyboard)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']

            if text == "Расписание":
                teacher_schedule_vk_bot(user_id)  # Функция для расписания преподавателя
            elif text == "Информация о студентах":
                # Здесь можно добавить логику для работы со студентами
                send_message(user_id, 'Функция в разработке.')

def ivent(user_id):
    keyboard = create_keyboard(['Новости МЕХМАТА', 'Новости ЮФУ', "Меню"], one_time=False)
    send_message(user_id, 'Выберите новость:', keyboard)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']

            if text == "Новости МЕХМАТА":
                send_message(user_id, student_get_news_mehmat())
            elif text == "Новости ЮФУ":
                send_message(user_id, student_get_news())
            elif text == "Меню":
                show_menu_student(user_id)

def schedule_vk_bot(user_id):
    # Получаем данные пользователя
    user = get_user("vk", user_id)

    # Проверяем, есть ли данные о курсе и группе
    if not user or 'course' not in user or 'group' not in user:
        send_message(user_id, 'Ошибка: Данные пользователя не найдены. Пройдите регистрацию заново.')
        return

    # Отправляем клавиатуру с выбором расписания
    keyboard = create_keyboard(['Сегодня', 'Завтра', 'Послезавтра', 'Неделя', 'Меню'])
    send_message(user_id, 'Выберите период:', keyboard)
    try:
        # Обработка выбора периода
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                text = event.obj.message['text']

                if text == 'Сегодня':
                    schedule_1 = str(get_schedule(user['course'], user['group'], 'today'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На сегодня расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))
                    # Выходим из цикла после обработки

                elif text == 'Завтра':
                    schedule_1 = str(get_schedule(user['course'], user['group'], 'tomorrow'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На завтра расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text == 'Послезавтра':
                    schedule_1 = str(get_schedule(user['course'], user['group'], 'atomorrow'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На послезавтра расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text == 'Неделя':
                    schedule_1 = str(get_schedule(user['course'], user['group'], 'week'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На неделю расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text.lower() == '/menu' or text.lower() == 'menu' or text.lower() == 'меню':
                    show_menu_student(user_id)

                else:
                    send_message(user_id, 'Пожалуйста, выберите период из предложенных вариантов.')
    except Exception as e:
        print(e)
        show_menu_student(user_id)

def teacher_schedule_vk_bot(user_id):
    send_message(user_id, 'Выберите период:', create_keyboard(['Сегодня', 'Завтра', 'Послезавтра', 'Неделя', 'Меню']))
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                text = event.obj.message['text']

                if text == 'Сегодня':
                    schedule_1 = str(get_teacher_schedule(user_id, 'today'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На сегодня расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text == 'Завтра':
                    schedule_1 = str(get_teacher_schedule(user_id, 'tomorrow'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На завтра расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text == 'Послезавтра':
                    schedule_1 = str(get_teacher_schedule(user_id, 'atomorrow'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На послезавтра расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text == 'Неделя':
                    schedule_1 = str(get_teacher_schedule(user_id, 'week'))
                    start_index = schedule_1.find("{")
                    end_index = schedule_1.rfind("}") + 1
                    schedule_data = ast.literal_eval(schedule_1[start_index:end_index])

                    if schedule_1 == {}:
                        send_message(user_id, 'На неделю расписания нет.')
                    else:
                        send_message(user_id, format_schedule(schedule_data))

                elif text.lower() == '/menu' or text.lower() == 'menu' or text.lower() == 'меню':
                    show_menu_teacher(user_id)

                else:
                    send_message(user_id, 'Пожалуйста, выберите период из предложенных вариантов.')
    except Exception as e:
        print(e)
        show_menu_teacher(user_id)

def teachher_schedule_vk_bot(user_id):
    send_message(user_id, 'Выберите период:', create_keyboard(['Сегодня', 'Завтра', 'Послезавтра', 'Неделя', 'Меню']))
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                text = event.obj.message['text']

                # Получаем данные преподавателя
                teacher_data = get_user("vk", user_id)
                if not teacher_data:
                    send_message(user_id, 'Ошибка: Данные преподавателя не найдены. Пройдите регистрацию заново.')
                    return

                teacher_name = teacher_data['name']  # Имя преподавателя

                if text == 'Сегодня':
                    schedule_data = get_teacher_schedule(teacher_name, 'today')
                elif text == 'Завтра':
                    schedule_data = get_teacher_schedule(teacher_name, 'tomorrow')
                elif text == 'Послезавтра':
                    schedule_data = get_teacher_schedule(teacher_name, 'atomorrow')
                elif text == 'Неделя':
                    schedule_data = get_teacher_schedule(teacher_name, 'week')
                elif text.lower() in ['/menu', 'menu', 'меню']:
                    show_menu_teacher(user_id)
                    return
                else:
                    send_message(user_id, 'Пожалуйста, выберите период из предложенных вариантов.')
                    continue

                # Проверяем, есть ли данные в расписании
                if not schedule_data:  # Если расписание пустое
                    send_message(user_id, 'На выбранный период расписания нет.')
                else:
                    # Форматируем и отправляем расписание
                    formatted_schedule = format_schedule(schedule_data)
                    send_message(user_id, formatted_schedule)

    except Exception as e:
        print(f"Ошибка: {e}")
        show_menu_teacher(user_id)
        send_message(user_id, 'Произошла ошибка. Пожалуйста, попробуйте позже.')


# Основной цикл бота
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        text = event.obj.message['text']

        if text.lower() == '/start' or text.lower() == 'start' or text.lower() == 'старт' or text.lower() == 'начать':
            # Отправляем сообщение с кнопкой "Начать" (одноразовая клавиатура)
            if get_user("vk", user_id):
                keyboard = create_keyboard(['Да', 'Нет'], inline=False)
                send_message(user_id, 'Вы хотите пройти процесс регистрации заново?', keyboard)
            else:
                keyboard = create_keyboard(['Студент', 'Абитуриент'], one_time=True)
                send_message(user_id, 'Вы студент или абитуриент?', keyboard)

        # Обработка ответа "Да" или "Нет" на вопрос о повторной регистрации
        elif text.lower() == 'да':
            # Если пользователь выбрал "Да", начинаем регистрацию заново
            keyboard = create_keyboard(['Студент', 'Абитуриент'], one_time=True)
            send_message(user_id, 'Вы студент или абитуриент?', keyboard)

        elif text.lower() == 'нет':
            # Если пользователь выбрал "Нет", показываем меню в зависимости от роли
            user_data = get_user("vk", user_id)  # Получаем данные пользователя
            if user_data is None:
                send_message(user_id, 'Ошибка: Пользователь не найден. Пройдите регистрацию заново.')
            elif user_data.get('is_abitur', False):  # Если пользователь — абитуриент
                show_menu_applicant(user_id)
            else:  # Если пользователь — студент
                show_menu_student(user_id)

        # Обработка выбора роли (студент или абитуриент)
        elif text == 'Студент':
            register(user_id, text)

        elif text == 'Абитуриент':
            register(user_id, text)

        # Если пользователь в процессе регистрации
        elif user_id in user_states:
            register(user_id, text)

        # Обработка команды меню
        elif text.lower() in ['/menu', 'menu', 'меню']:
            # Показываем меню в зависимости от роли
            user_data = get_user("vk", user_id)
            if not user_data:
                send_message(user_id, 'Ошибка: Пользователь не найден. Пройдите регистрацию заново.')
            elif user_data['is_abitur']:  # Если пользователь — абитуриент
                show_menu_applicant(user_id)
            else:  # Если пользователь — студент или преподаватель
                show_menu_student(user_id)  # Пока что используем меню для студентов
