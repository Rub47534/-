import telebot
from telebot import types
bot = telebot.TeleBot('7724212735:AAH15oMo7CyoPszRzdRrHSwXMgrL0N0UnSk')
import sqlite3

conn = sqlite3.connect('C:\SQL_Studio\Database_Bot', check_same_thread=False)
cursor = conn.cursor()

# Состояние регистрации
registration_in_progress = {}

# All functions in window
rating = "🏆 Рейтинг"
current_task = "📊 Текущее задание"
registration_worker = "📝 Регистрация работника"
registration_admins = "👨‍💻Регистрация администратора"

#Все переменные
admin_id_num = 1
worker_id_num = 1

def db_table_workers(user_id: int, user_name: str, user_surname: str, middle_name: str, team_name: str, position_name: str,
                 password: str):
    cursor.execute(
        'INSERT INTO workers (user_id, user_name, user_surname, middle_name, team_name, position_name, password) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, user_name, user_surname, middle_name, team_name, position_name, password))
    conn.commit()

def db_table_val_admins(user_id: int, user_name: str, user_surname: str, middle_name: str, password: str):
    cursor.execute(
        'INSERT INTO admins (user_id, user_name, user_surname, middle_name, password) VALUES (?, ?, ?, ?, ?)',
        (user_id, user_name, user_surname, middle_name, password))
    conn.commit()

def db_table_row_read(target_id: int):
    cursor.execute("SELECT * FROM workers WHERE id = ?", (target_id,))

@bot.message_handler(func=lambda message: message.text not in ["Start", rating, current_task, registration_worker, registration_admins])
def first_interaction(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_button = types.KeyboardButton("Start")
    markup.add(start_button)
    bot.send_message(message.chat.id, "Нажми кнопку 'Start', чтобы начать:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Start")
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(rating)
    button2 = types.KeyboardButton(current_task)
    button3 = types.KeyboardButton(registration_worker)
    button4 = types.KeyboardButton(registration_admins)
    markup.add(button1, button2, button3, button4)
    bot.send_message(message.chat.id, "Что тебе нужно, воин?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == rating)
def check_rating(message):
    bot.send_message(message.chat.id, "Укажи свой id")
    bot.register_next_step_handler(message, get_rating)

def get_rating(message):
    tar_id = message.text
    db_table_row_read(target_id=tar_id)
    row = cursor.fetchone()
    bot.send_message(message.chat.id, f"Запрос выполнен!\nid: {tar_id}\nИнформация: {row}")

@bot.message_handler(func=lambda message: message.text == current_task)
def check_task(message):
    bot.send_message(message.chat.id, "В работе...")

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
        return  # Если регистрация прервана, ничего не делаем
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

def complete_registration(message, user_id):
    global worker_id_num
    user_data = get_user_data(user_id)
    if not user_data:
        bot.send_message(message.chat.id, "Ошибка: данные пользователя не найдены.")
        return
    bot.send_message(
        message.chat.id,
        f"Регистрация завершена!\n"
        f"Имя: {user_data['name']}\nФамилия: {user_data['surname']}\n"
        f"Отчество: {user_data['middle_name']}\nКоманда: {user_data['team_name']}\n"
        f"Должность: {user_data['position']}\nID: {s}"
    )
    db_table_workers(
        user_id=worker_id_num,
        user_name=user_data['name'],
        user_surname=user_data['surname'],
        middle_name=user_data['middle_name'],
        team_name=user_data['team_name'],
        position_name=user_data['position'],
        password=user_data['password']
    )
    worker_id_num += 1
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
    global admin_id_num
    user_data = get_user_data(user_id)
    if not user_data:
        bot.send_message(message.chat.id, "Ошибка: данные пользователя не найдены.")
        return
    bot.send_message(
        message.chat.id,
        f"Регистрация администратора завершена!\n"
        f"Имя: {user_data['name']}\nФамилия: {user_data['surname']}\n"
        f"Отчество: {user_data['middle_name']}\nID: {s}"
    )
    db_table_val_admins(
        user_id=admin_id_num,
        user_name=user_data['name'],
        user_surname=user_data['surname'],
        middle_name=user_data['middle_name'],
        password=user_data['password']
    )
    admin_id_num += 1
    main_menu(message)

bot.polling(none_stop=True)
