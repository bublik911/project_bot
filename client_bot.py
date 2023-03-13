import pymysql
import telebot
from telebot import types
from connetion import connection

client_bot = telebot.TeleBot('5296562344:AAFRkKZdWqM8untSCYqyHjppB1bHsL9aNKM')


def phone_number(x):
    s = str(x)
    phone = ''
    for i in s:
        if i.isdigit():
            phone += i
    phone = phone[-10:]
    return phone


@client_bot.message_handler(commands=['start'])
def start(message):
    mes = client_bot.send_message(message.chat.id, 'Введите свой номер телефона, чтобы получать рассылку от своего консультанта')
    client_bot.register_next_step_handler(mes, phone_client_update)


def phone_client_update(message):
    user_id = str(message.chat.id)
    num = phone_number(str(message.text))
    if len(num) < 10:
        client_bot.send_message(message.chat.id, 'Введите корректный номер. Например: 8-(777)-777-77-77')
    else:
        with connection.cursor() as cursor:
            num_counter = cursor.execute(f"SELECT * FROM client_base WHERE phone = {num}")
            if num_counter == 0:
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
                markup.add(btn)
                client_bot.send_message(message.chat.id, 'Обратитесь к своему консультанту или администратору, чтобы вас добавили в базу', reply_markup=markup)
            elif num_counter == 1:
                with connection.cursor() as cursor:
                    cursor.execute(f"UPDATE client_base SET chat_id = {user_id} WHERE phone = {num}")
                    connection.commit()
                client_bot.send_message(message.chat.id, 'Спасибо! Ожидайте сообщений)')
            else:
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
                markup.add(btn)
                client_bot.send_message(message.chat.id, 'Обнаружена ошибка! Обратитесь к администратору.', reply_markup=markup)


client_bot.polling(non_stop=True)