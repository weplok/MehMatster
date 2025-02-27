import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

# Токен группы и ID группы
GROUP_TOKEN = 'vk1.a.Eh3cWTw6_fK8c6Ehs6eSP7iMZUafALpGMNivdc5xuHjYKlE4_VOLDK9dTHYG_fmhuWv78Ln8ivKH9wJubNFBCYsWGOik0SoCmL7fBHTkfEioTfHfCUzaTgAm1gRqVUC0dXne7dN_CcoXgLE-MoepOysg5Gy5fO2Gsotig0FMTJbMSneQsk-8G7qYE5Cd7igkZPg8n1tjTLv_TqqzaDzevg'
GROUP_ID = '229555438'  # Только цифры

# Инициализация бота
vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# Функция для создания клавиатуры
def create_keyboard(buttons, inline=False):
    keyboard = vk_api.keyboard.VkKeyboard(one_time=False, inline=inline)
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

        if text.lower() == 'начать':
            # Отправляем сообщение с кнопкой "Начать"
            keyboard = create_keyboard(['Начать'])
            send_message(user_id, 'Привет! Я твой бот. Нажми на кнопку ниже.', keyboard)

        elif text == 'Начать':
            # Спрашиваем, авторизован ли пользователь
            keyboard = create_keyboard(['Уже авторизован', 'Авторизация'], inline=True)
            send_message(user_id, 'Вы уже авторизованы или хотите авторизоваться?', keyboard)

        elif text == 'Авторизация':
            # Спрашиваем, студент или абитуриент
            keyboard = create_keyboard(['Студент', 'Абитуриент'], inline=True)
            send_message(user_id, 'Вы студент или абитуриент?', keyboard)

        elif text == 'Студент':
            # Запрашиваем данные студента
            send_message(user_id, 'Пожалуйста, введите ваши данные в формате: ФИО, группа, курс.')

        elif text == 'Абитуриент':
            # Предлагаем выбор: Условие, Финансы, Инфраструктура
            keyboard = create_keyboard(['Условие', 'Финансы', 'Инфраструктура'])
            send_message(user_id, 'Выберите интересующий вас раздел:', keyboard)

        elif text == 'Финансы':
            # Предлагаем выбор: Бюджет, Платное
            keyboard = create_keyboard(['Бюджет', 'Платное'], inline=True)
            send_message(user_id, 'Выберите тип обучения:', keyboard)

        elif text == 'Бюджет':
            # Сообщение для выбора "Бюджет"
            send_message(user_id, 'Вы выбрали "Бюджет". Обучение на бюджетной основе.')

        elif text == 'Платное':
            # Сообщение для выбора "Платное"
            send_message(user_id, 'Вы выбрали "Платное". Обучение на платной основе.')

        elif text == 'Инфраструктура':
            # Предлагаем выбор: Общага, Кампус
            keyboard = create_keyboard(['Общага', 'Кампус'], inline=True)
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
            keyboard = create_keyboard(['Сегодня', 'Завтра', 'Неделя'])
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
            keyboard = create_keyboard(['Последние новости', 'Ссылка на ТГ'], inline=True)
            send_message(user_id, 'Выберите действие:', keyboard)

        elif text == 'Последние новости':
            # Сообщение для выбора "Последние новости"
            send_message(user_id, 'Последние новости: ...')

        elif text == 'Ссылка на ТГ':
            # Сообщение с ссылкой на Telegram
            send_message(user_id, 'Перейдите по ссылке: https://t.me/your_telegram_channel')

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
