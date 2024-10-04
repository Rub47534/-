import telebot
from telebot import types
bot = telebot.TeleBot('7724212735:AAH15oMo7CyoPszRzdRrHSwXMgrL0N0UnSk')
import sqlite3
import requests
import random

KAITEN_API_URL = 'https://karavayk.kaiten.ru/api/latest/cards'
# URL API Kaiten
KAITEN_API_TOKEN = 'eb04363c-7d76-48fc-ab7b-cd140b7190db'
conn = sqlite3.connect('C:\SQL_Studio\Database_Bot', check_same_thread=False)
cursor = conn.cursor()
BOARD_ID = 1044429
LIMIT = 200

# Состояние регистрации
registration_in_progress = {}

# All functions in window
rating = "🏆 Рейтинг"
current_task = "📊 Текущее задание"
registration_worker = "📝 Регистрация работника"
registration_admins = "👨‍💻Регистрация администратора"
for_admin = "🕵️‍♂️Для администратора"


def db_table_workers(user_name: str, user_surname: str, middle_name: str, team_name: str, position_name: str,
                 password: str):
    cursor.execute(
        'INSERT INTO workers (user_name, user_surname, middle_name, team_name, position_name, password) VALUES (?, ?, ?, ?, ?, ?)',
        (user_name, user_surname, middle_name, team_name, position_name, password))
    conn.commit()

def db_table_val_admins(user_name: str, user_surname: str, middle_name: str, password: str):
    cursor.execute(
        'INSERT INTO admins (user_name, user_surname, middle_name, password) VALUES (?, ?, ?, ?)',
        (user_name, user_surname, middle_name, password))
    conn.commit()

def db_table_row_read(target_id: int):
    cursor.execute("SELECT * FROM workers WHERE id = ?", (target_id,))

@bot.message_handler(func=lambda message: message.text not in ["Start", rating, current_task, registration_worker, registration_admins, for_admin])
def first_interaction(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_button = types.KeyboardButton("Start")
    markup.add(start_button)
    bot.send_message(message.chat.id, "Нажми кнопку 'Start', чтобы начать:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Start")
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(registration_worker)
    button2 = types.KeyboardButton(current_task)
    button3 = types.KeyboardButton(rating)
    button4 = types.KeyboardButton(registration_admins)
    button5= types.KeyboardButton(for_admin)
    markup.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id, "Что тебе нужно, воин?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == rating)
def check_rating(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    worker_button = types.KeyboardButton("🔨Работник")
    admin_button = types.KeyboardButton("📅Администратор")
    markup.add(worker_button, admin_button)

    bot.send_message(message.chat.id, "Кем вы являетесь?", reply_markup=markup)
    bot.register_next_step_handler(message, choose_role)

def choose_role(message):
    if message.text == "🔨Работник":
        ask_worker_surname(message)
    elif message.text == "📅Администратор":
        bot.send_message(message.chat.id, "Проверка для администратора в разработке.")
        main_menu(message)
    else:
        main_menu(message)
worker_data = {}

def ask_worker_surname(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить")
    markup.add(cancel_button)
    bot.send_message(message.chat.id, "Введите свою фамилию:", reply_markup=markup)
    bot.register_next_step_handler(message, process_worker_surname)

def process_worker_surname(message):
    if message.text == "❌ Отменить":
        main_menu(message)
    else:
        worker_data['surname'] = message.text
        ask_worker_password(message)

def ask_worker_password(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить")
    markup.add(cancel_button)

    bot.send_message(message.chat.id, "Введите ваш пароль:", reply_markup=markup)
    bot.register_next_step_handler(message, process_worker_password)

def process_worker_password(message):
    if message.text == "❌ Отменить":
        main_menu(message)
    else:
        worker_data['password'] = message.text
        check_worker_credentials(message)

def check_worker_credentials(message):
    surname = worker_data['surname']
    password = worker_data['password']
    cursor.execute("SELECT * FROM Workers WHERE user_surname = ?", (surname,))
    worker_row = cursor.fetchone()
    if worker_row:
        db_password = worker_row[6]
        if password == db_password:
            rating = worker_row[7]
            if (rating == 1):
                bot.send_message(message.chat.id, f"Ваш рейтинг: {rating} 🏆")
            elif (rating == 2):
                bot.send_message(message.chat.id, f"Ваш рейтинг: {rating} 🥈")
            elif (rating == 3):
                bot.send_message(message.chat.id, f"Ваш рейтинг: {rating} 🥉")
            elif (rating > 3):
                bot.send_message(message.chat.id, f"Ваш рейтинг: {rating}")
            main_menu(message)
        else:
            bot.send_message(message.chat.id, "Неверный пароль. Чтобы ввести заново, отправьте любое сообщение")
            bot.register_next_step_handler(message, ask_worker_password)
    else:
        bot.send_message(message.chat.id, "Фамилия не найдена. Чтобы ввести заново, отправьте любое сообщение.")
        bot.register_next_step_handler(message, ask_worker_surname)

@bot.message_handler(func=lambda message: message.text == current_task)
def start_task_check(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить")
    markup.add(cancel_button)
    bot.send_message(message.chat.id, "Введите вашу фамилию:", reply_markup=markup)
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    if message.text == "❌ Отменить":
        cancel_process(message)
        return
    surname = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить")
    markup.add(cancel_button)
    bot.send_message(message.chat.id, "Введите ваш пароль:", reply_markup=markup)
    bot.register_next_step_handler(message, get_password, surname)

def get_password(message, surname):
    if message.text == "❌ Отменить":
        cancel_process(message)
        return
    password = message.text
    if authenticate_and_show_cards(message, surname, password):
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Неверная фамилия или пароль. Попробуйте снова.")
        main_menu(message)

def authenticate_and_show_cards(message, surname, password):
    cursor.execute("SELECT id, password FROM workers WHERE user_surname = ?", (surname,))
    worker = cursor.fetchone()
    if worker is None:
        bot.send_message(message.chat.id, "Пользователь с такой фамилией не найден.")
        return False
    worker_id, stored_password = worker
    if password != stored_password:
        bot.send_message(message.chat.id, "Неверный пароль.")
        return False
    assign_random_user_ids()
    cursor.execute("""
        SELECT card_title 
        FROM KaitenCards 
        WHERE id_user = ?
    """, (worker_id,))
    cards = cursor.fetchall()
    if cards:
        bot.send_message(message.chat.id, f"Карточки, назначенные вам:")
        for card in cards:
            bot.send_message(message.chat.id, f"- {card[0]}")
    else:
        bot.send_message(message.chat.id, f"Для вас карточки не найдены.")
    return True

def assign_random_user_ids():
    cursor.execute("SELECT id FROM workers")
    worker_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT card_id FROM KaitenCards")
    card_ids = [row[0] for row in cursor.fetchall()]
    if not worker_ids or not card_ids:
        print("Нет работников или карточек для присвоения.")
        return
    random.shuffle(worker_ids)
    for index, card_id in enumerate(card_ids):
        user_id = worker_ids[index % len(worker_ids)]
        cursor.execute("UPDATE KaitenCards SET id_user = ? WHERE card_id = ?", (user_id, card_id))
    conn.commit()
    print("ID пользователей успешно присвоены карточкам.")

def cancel_process(message):
    bot.send_message(message.chat.id, "Процесс отменён.")
    main_menu(message)

# Регистрация работника
@bot.message_handler(func=lambda message: message.text == registration_worker)
def register_user(message):
    registration_in_progress[message.chat.id] = True
    data = {}
    save_user_data(message.chat.id, data)
    ask_next_step(message, "Введите своё имя:", 'name', data)

def ask_next_step(message, text, field, data):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить регистрацию")
    markup.add(cancel_button)
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, process_step, field, data)

def process_step(message, field, data):
    if message.chat.id not in registration_in_progress:
        return
    if message.text == "❌ Отменить регистрацию":
        cancel_registration(message)
        return
    data[field] = message.text
    save_user_data(message.chat.id, data)
    next_steps = {
        'name': ("Введите свою фамилию:", 'surname'),
        'surname': ("Введите своё отчество:", 'middle_name'),
        'middle_name': ("Введите название команды:", 'team_name'),
        'team_name': ("Введите вашу должность в проекте:", 'position'),
        'position': ("Придумайте пароль:", 'password'),
    }
    if field in next_steps:
        ask_next_step(message, *next_steps[field], data)
    elif field == 'password':
        bot.send_message(message.chat.id, "Введите пароль ещё раз для подтверждения:")
        bot.register_next_step_handler(message, confirm_password, data)

def confirm_password(message, data):
    if message.text == data['password']:
        show_confirmation(message, data)
    else:
        bot.send_message(message.chat.id, "Пароли не совпадают. Попробуйте снова.")
        bot.send_message(message.chat.id, "Придумайте пароль заново:")
        bot.register_next_step_handler(message, retry_password, data)

def retry_password(message, data):
    data['password'] = message.text
    save_user_data(message.chat.id, data)
    bot.send_message(message.chat.id, "Введите пароль ещё раз для подтверждения:")
    bot.register_next_step_handler(message, confirm_password_retry, data)

def confirm_password_retry(message, data):
    if message.text == data['password']:
        show_confirmation(message, data)
    else:
        bot.send_message(message.chat.id, "Пароли снова не совпадают. Попробуем ещё раз.")
        retry_password(message, data)

def show_confirmation(message, data):
    markup = types.InlineKeyboardMarkup()
    btn_correct = types.InlineKeyboardButton("✅Всё верно", callback_data="correct")
    btn_incorrect = types.InlineKeyboardButton("❌Неверно", callback_data="incorrect")
    markup.add(btn_correct, btn_incorrect)
    bot.send_message(
        message.chat.id,
        f"Проверьте введённые данные:\n"
        f"Имя: {data['name']}\nФамилия: {data['surname']}\n"
        f"Отчество: {data['middle_name']}\nКоманда: {data['team_name']}\n"
        f"Должность: {data['position']}",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["correct", "incorrect"])
def callback_query(call):
    if call.data == "correct":
        complete_registration(call.message, call.message.chat.id)
    elif call.data == "incorrect":
        bot.send_message(call.message.chat.id, "Давайте попробуем снова.")
        register_user(call.message)

def get_last_worker_id():
    cursor.execute("SELECT MAX(id) FROM workers")
    worker_id = cursor.fetchone()[0]
    return worker_id

def create_worker_table(worker_id: int):
    table_name = f"worker_data_{worker_id}"
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            task_description TEXT,
            task_status TEXT,
            deadline TEXT,
            Level_task INTEGER,
            Score INTEGER  
        )
    """)
    conn.commit()

def insert_worker_data(worker_id: int, task_name: str, task_description: str, task_status: str, deadline: str, level_task: int, score: int ):
    table_name = f"worker_data_{worker_id}"
    cursor.execute(f"""
        INSERT INTO {table_name} (task_name, task_description, task_status, deadline, level_task, score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_name, task_description, task_status, deadline, level_task, score))
    conn.commit()

def register_table_for_worker():
    new_user_id = get_last_worker_id()
    create_worker_table(new_user_id)
    insert_worker_data(new_user_id,"Задача 1", "Описание задачи 1","Статус", "Дедлайн 1", 2, 1)

def complete_registration(message, user_id):
    user_data = get_user_data(user_id)
    if not user_data:
        bot.send_message(message.chat.id, "Ошибка: данные пользователя не найдены.")
        return
    bot.send_message(
        message.chat.id,
        f"Регистрация завершена!\n"
        f"Имя: {user_data['name']}\nФамилия: {user_data['surname']}\n"
        f"Отчество: {user_data['middle_name']}\nКоманда: {user_data['team_name']}\n"
        f"Должность: {user_data['position']}"
    )
    db_table_workers(
        user_name=user_data['name'],
        user_surname=user_data['surname'],
        middle_name=user_data['middle_name'],
        team_name=user_data['team_name'],
        position_name=user_data['position'],
        password=user_data['password']
    )
    register_table_for_worker()
    main_menu(message)
users_data = {}

def get_user_data(user_id):
    return users_data.get(user_id)

def save_user_data(user_id, data):
    users_data[user_id] = data

def cancel_registration(message):
    if message.chat.id in registration_in_progress:
        del registration_in_progress[message.chat.id]
        bot.send_message(message.chat.id, "Регистрация пользователя отменена")
        main_menu(message)

# Регистрация администратора
@bot.message_handler(func=lambda message: message.text == registration_admins)
def register_admin(message):
    registration_in_progress[message.chat.id] = True
    data = {}
    save_user_data(message.chat.id, data)
    ask_next_step_admin(message, "Введите своё имя:", 'name', data)

def ask_next_step_admin(message, text, field, data):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить регистрацию")
    markup.add(cancel_button)
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, process_step_admin, field, data)

def process_step_admin(message, field, data):
    if message.chat.id not in registration_in_progress:
        return
    if message.text == "❌ Отменить регистрацию":
        cancel_registration(message)
        return
    data[field] = message.text
    save_user_data(message.chat.id, data)
    next_steps = {
        'name': ("Введите свою фамилию:", 'surname'),
        'surname': ("Введите своё отчество:", 'middle_name'),
        'middle_name': ("Придумайте пароль:", 'password'),
    }
    if field in next_steps:
        ask_next_step_admin(message, *next_steps[field], data)
    elif field == 'password':
        bot.send_message(message.chat.id, "Введите пароль ещё раз для подтверждения:")
        bot.register_next_step_handler(message, confirm_password_admin, data)

def confirm_password_admin(message, data):
    if message.text == data['password']:
        show_confirmation_admin(message, data)
    else:
        bot.send_message(message.chat.id, "Пароли не совпадают. Попробуйте снова.")
        bot.send_message(message.chat.id, "Придумайте пароль заново:")
        bot.register_next_step_handler(message, retry_password_admin, data)

def retry_password_admin(message, data):
    data['password'] = message.text
    save_user_data(message.chat.id, data)
    bot.send_message(message.chat.id, "Введите пароль ещё раз для подтверждения:")
    bot.register_next_step_handler(message, confirm_password_retry_admin, data)

def confirm_password_retry_admin(message, data):
    if message.text == data['password']:
        show_confirmation_admin(message, data)
    else:
        bot.send_message(message.chat.id, "Пароли снова не совпадают. Попробуем ещё раз.")
        retry_password_admin(message, data)

def show_confirmation_admin(message, data):
    markup = types.InlineKeyboardMarkup()
    btn_correct = types.InlineKeyboardButton("✅ Всё верно", callback_data="correct_admin")
    btn_incorrect = types.InlineKeyboardButton("❌ Неверно", callback_data="incorrect_admin")
    markup.add(btn_correct, btn_incorrect)
    bot.send_message(
        message.chat.id,
        f"Проверьте введённые данные:\n"
        f"Имя: {data['name']}\nФамилия: {data['surname']}\n"
        f"Отчество: {data['middle_name']}",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["correct_admin", "incorrect_admin"])
def callback_query_admin(call):
    if call.data == "correct_admin":
        complete_registration_admin(call.message, call.message.chat.id)
    elif call.data == "incorrect_admin":
        bot.send_message(call.message.chat.id, "Давайте попробуем снова.")
        register_admin(call.message)

def complete_registration_admin(message, user_id):
    user_data = get_user_data(user_id)
    if not user_data:
        bot.send_message(message.chat.id, "Ошибка: данные пользователя не найдены.")
        return
    bot.send_message(
        message.chat.id,
        f"Регистрация администратора завершена!\n"
        f"Имя: {user_data['name']}\nФамилия: {user_data['surname']}\n"
        f"Отчество: {user_data['middle_name']}"
    )
    db_table_val_admins(
        user_name=user_data['name'],
        user_surname=user_data['surname'],
        middle_name=user_data['middle_name'],
        password=user_data['password']
    )
    main_menu(message)


# Обработка кнопки "Для администраторов"
@bot.message_handler(func=lambda message: message.text == for_admin)
def admin_registration(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton("❌ Отменить")
    markup.add(cancel_button)
    bot.send_message(message.chat.id, "Введите вашу фамилию:", reply_markup=markup)
    bot.register_next_step_handler(message, process_admin_surname)

def process_admin_surname(message):
    if message.text == "❌ Отменить":
        cancel_action(message)
        return
    surname = message.text
    bot.send_message(message.chat.id, "Введите ваш пароль:")
    bot.register_next_step_handler(message, process_admin_password, surname)

def process_admin_password(message, surname):
    if message.text == "❌ Отменить":
        cancel_action(message)
        return
    password = message.text
    cursor.execute("""
        SELECT * FROM admins
        WHERE user_surname = ? AND password = ?
    """, (surname, password))
    admin_info = cursor.fetchone()
    if admin_info:
        bot.send_message(message.chat.id, "Регистрация подтверждена. Добро пожаловать, администратор!")
        check_task(message)
    else:
        bot.send_message(message.chat.id, "Ошибка! Неверная фамилия или пароль.")
        main_menu(message)

def cancel_action(message):
    bot.send_message(message.chat.id, "Действие отменено.")
    main_menu(message)

def check_task(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    worker_info_button = types.KeyboardButton("📇Информация о работнике")
    team_info_button = types.KeyboardButton("📢Информация о команде")
    team_list_button = types.KeyboardButton("📚Список команд")
    rating_table_button = types.KeyboardButton("🏅Рейтинговая таблица")
    task_list = types.KeyboardButton("📋Список задач")
    cancel_menu = types.KeyboardButton("🔙Назад в меню")
    markup.add(worker_info_button, team_info_button, team_list_button, rating_table_button,task_list, cancel_menu)
    bot.send_message(message.chat.id, "Какая информация вас интересует?", reply_markup=markup)
    bot.register_next_step_handler(message, handle_admin_choice)

def handle_admin_choice(message):
    if message.text == "📇Информация о работнике":
        bot.send_message(message.chat.id, "Введите фамилию работника:")
        bot.register_next_step_handler(message, get_worker_info)
    elif message.text == "📢Информация о команде":
        get_team_info(message)
    elif message.text == "📚Список команд":
        show_team_list(message)
    elif message.text == "🏅Рейтинговая таблица":
        show_rating_table(message)
    elif message.text == "📋Список задач":
        show_list_task(message)
    elif message.text == "🔙Назад в меню":
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Выберите корректный вариант.")
        check_task(message)

def get_worker_info(message):
    surname = message.text
    cursor.execute("""
            SELECT id, user_name, user_surname, middle_name, team_name, position_name, password, rating
            FROM workers
            WHERE user_surname = ?
        """, (surname,))
    worker_info = cursor.fetchone()
    if worker_info:
        bot.send_message(
            message.chat.id,
            f"Информация о работнике:\n"
            f"ID: {worker_info[0]}\n"
            f"Имя: {worker_info[1]}\n"
            f"Фамилия: {worker_info[2]}\n"
            f"Отчество: {worker_info[3]}\n"
            f"Команда: {worker_info[4]}\n"
            f"Должность: {worker_info[5]}\n"
            f"Пароль: {worker_info[6]}\n"
            f"Рейтинг: {worker_info[7]}"
        )
    else:
        bot.send_message(message.chat.id, "Работник с такой фамилией не найден.")
    check_task(message)

def get_team_info(message):
    bot.send_message(message.chat.id, "Находится в работе...")
    check_task(message)

def show_team_list(message):
    bot.send_message(message.chat.id, "Находится в работе...")
    check_task(message)

def show_rating_table(message):
    bot.send_message(message.chat.id, "Находится в работе...")
    check_task(message)

def show_list_task(message):
    clear_bd_kaiten(message)
    headers = {
        'Authorization': f'Bearer {KAITEN_API_TOKEN}',
        #        'board_id' : BOARD_ID
    }

    try:
        response = requests.get(KAITEN_API_URL, headers=headers, params={'board_id': BOARD_ID, 'limit': LIMIT})
        response.raise_for_status()  # Проверка на ошибки HTTP
        cards_data = response.json()
        cards_list = [(i['id'], i['title']) for i in cards_data]
        #        list_of_cards_titles = [i['title'] for i in cards_data]

        cursor.executemany("INSERT INTO KaitenCards (card_id, card_title) VALUES (?, ?)", cards_list)
        conn.commit()
        print(cards_list)
        #       print(list_of_cards_titles)

        """
        # Проверьте вашу структуру данных
        if isinstance(cards_data, dict) and 'cards' in cards_data:  # Проверяем, что это словарь и есть ключ 'cards'
            if cards_data['cards']:  # Если возвращен список карточек
                card_list = "\n".join([f"id: {card['id']}, title: {card['title']}" for card in cards_data['cards']])
                bot.reply_to(message, f"Вот список карточек:\n{card_list}")
            else:
                bot.reply_to(message, "Карточки не найдены.")
        else:
            bot.reply_to(message, "Некорректный ответ от API.")
            print(list_of_cards_ids)

        """

    except requests.exceptions.HTTPError as err:
        bot.reply_to(message, f"Ошибка при обращении к Kaiten API: {err}")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
    read_tasks(message)
    check_task(message)

def clear_bd_kaiten (message):
        try:
            cursor.execute("DELETE FROM KaitenCards")
            conn.commit()
        except Exception as e:
            # Сообщение об ошибке
            bot.send_message(message.chat.id, f"Произошла ошибка при очистке таблицы: {str(e)}")
            conn.rollback()

def read_tasks(message):
    try:
        cursor.execute("SELECT card_id, card_title FROM KaitenCards")
        records = cursor.fetchall()
        if records:
            response = "Список активных карт:\n"
            response = "    ID                  Название\n"
            for record in records:
                response += f"{record[0]}   {record[1]}\n"
        else:
            response = "Таблица KaitenCards пуста."
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при получении данных: {str(e)}")

bot.polling(none_stop=True)
