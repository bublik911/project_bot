import telebot
from datetime import datetime
from telebot import types
from connetion import connection

info_client_dict = {}
month = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
bot = telebot.TeleBot('5408757344:AAFGtHco9x9xdezFeadsV6aGe7rPAjijRqg')


def phone_number(x):
    s = str(x)
    phone = ''
    for i in s:
        if i.isdigit():
            phone += i
    phone = phone[-10:]
    return phone


def insert_info(a, b, c, d, e):
    with connection.cursor() as cursor:
        add_info = f"INSERT INTO client_base (pid, name, phone, date, app) VALUES ({a}, '" + b +"', '" + c + "', '" + d +"', '" + e +"')"
        cursor.execute(add_info)
        connection.commit()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
    markup.add(btn)
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}! Я буду помогать Вам делать рассылку клиентам, работающих с Вами! Если вам нужна помощь, обратитесь к нашему администратору. Он сможет вам помочь!",reply_markup=markup)
    mes = bot.send_message(message.chat.id, 'Введите свой номер телефона для идентификации пользователя')
    bot.register_next_step_handler(mes, init)


def init(message):
    phone = str(message.text)
    phone = phone_number(phone)
    if len(phone) < 10:
        mes = bot.send_message(message.chat.id, 'Введите корректный номер. Например: 8-(777)-777-77-77')
        bot.register_next_step_handler(mes, init)
    else:
        with connection.cursor() as cursor:
            check_info = cursor.execute("SELECT * FROM client_base WHERE phone= '" + phone + "'")
            if check_info == 0:
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
                markup.add(btn)
                bot.send_message(message.chat.id, 'Обратитесь к администратору для покупки доступа к базе', reply_markup=markup)
            elif check_info == 1:
                user_id = str(message.chat.id)
                with connection.cursor() as cursor:
                    check_info = "UPDATE client_base SET chat_id= '" + user_id + "' WHERE phone = '" + phone + "'"
                    cursor.execute(check_info)
                    connection.commit()
                menu(message)
            else:
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
                markup.add(btn)
                bot.send_message(message.chat.id, 'Обнаружена ошибка! Обратитесь к администратору.', reply_markup=markup)


def menu(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📕Проверить клиентскую базу')
    btn2 = types.KeyboardButton('✏Добавить клиента')
    btn3 = types.KeyboardButton('✉Рассылка')
    markup.add(btn2, btn3, btn1)
    mes = bot.send_message(message.chat.id, 'Это главное меню. Что вы хотите сделать сейчас?', reply_markup=markup)
    bot.register_next_step_handler(mes, answer_client)


@bot.message_handler(content_types=['text'])
def answer_client(message):
    if message.text == '✏Добавить клиента' or message.text == 'Да' or message.text == 'Заполнить заново':
        a = types.ReplyKeyboardRemove()
        mes = bot.send_message(message.chat.id, 'Введите имя клиента', reply_markup=a)
        bot.register_next_step_handler(mes, name_client)
    elif message.text == 'Нет, спасибо':
        menu(message)
    elif message.text == '📕Проверить клиентскую базу':
        user_id = str(message.chat.id)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM client_base WHERE chat_id = {user_id}")
            row = cursor.fetchone()
            id = row.get('id')
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM client_base WHERE pid = {id} and deleted_at is null")
            base = cursor.fetchall()
            info = []
            for i in range(len(base)):
                line = base[i]
                num = str(i + 1)
                name_cl = line.get('name')
                phone_cl = '+7' + line.get('phone')
                date_cl = str(line.get('date')).split()
                date_ymd = date_cl[0].split('-')
                date_m = date_ymd[1]
                date_d = date_ymd[2]
                info.append(num + ') ' + name_cl + '  Д/р (день.месяц):  ' + date_d + '.' + date_m + '\n'
                            'Тел.:  ' + phone_cl)
            bot.send_message(message.chat.id, '\n'.join(info))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton('Все верно')
            btn2 = types.KeyboardButton('Удалить клиента из базы')
            markup.add(btn1, btn2)
            mes = bot.send_message(message.chat.id, 'Проверьте клиентскую базу', reply_markup=markup)
            bot.register_next_step_handler(mes, answer_base)
            info.clear()
    elif message.text == '✉Рассылка':
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
        markup.add(btn)
        bot.send_message(message.chat.id, 'Рассылка - функция, которую предоставляет консультантам бот. По умолчанию для всех групп клиентов сообщение начинается с приветствия: "Здраствуйте, (имя клиента)!". \n'
                                          'Если вы хотите изменить приветственный блок сообщения, обратитесь к администратору', reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn = types.KeyboardButton('Рассылка всем клиентам')
        btn1 = types.KeyboardButton('Рассылка ко дню рождения')
        markup.add(btn, btn1)
        mes = bot.send_message(message.chat.id, 'Текст рассылки для какой группы вы хотите задать?', reply_markup=markup)
        bot.register_next_step_handler(mes, answer_sender)


def answer_base(message):
    if message.text == 'Все верно':
        menu(message)
    elif message.text == 'Удалить клиента из базы':
        a = types.ReplyKeyboardRemove()
        mes = bot.send_message(message.chat.id, 'Введите номер телефона клиента которого хотите удалить', reply_markup=a)
        bot.register_next_step_handler(mes, delete)


def delete(message):
    phone = phone_number(message.text)
    delete_date = str(datetime.now()).split()
    delete_date = delete_date[0]
    with connection.cursor() as cursor:
        cursor.execute("UPDATE client_base SET deleted_at = '" + delete_date + "' WHERE phone = '" + phone + "'")
        connection.commit()
    bot.send_message(message.chat.id, 'Клиент удален')
    menu(message)


def name_client(message):
    user_id = str(message.chat.id)
    info_client_dict.setdefault(user_id, [])
    name = str(message.text)
    info_client_dict[user_id].append(name)
    mes = bot.send_message(message.chat.id, 'Введите номер телефона клиента')
    bot.register_next_step_handler(mes, phone_client)


def phone_client(message):
    user_id = str(message.chat.id)
    phone = phone_number(str(message.text))
    if len(phone) < 10:
        mes = bot.send_message(message.chat.id, 'Введите корректный номер телефона. Например: 8-(777)-777-77-77')
        bot.register_next_step_handler(mes, phone_client)
    else:
        info_client_dict[user_id].append(phone)
        date_client_month(message)


def date_client_month(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    jan = types.KeyboardButton('Январь')
    feb = types.KeyboardButton('Февраль')
    mar = types.KeyboardButton('Март')
    apr = types.KeyboardButton('Апрель')
    may = types.KeyboardButton('Май')
    june = types.KeyboardButton('Июнь')
    july = types.KeyboardButton('Июль')
    aug = types.KeyboardButton('Август')
    sep = types.KeyboardButton('Сентябрь')
    october = types.KeyboardButton('Октябрь')
    nov = types.KeyboardButton('Ноябрь')
    dec = types.KeyboardButton('Декабрь')
    markup.add(jan,feb,mar,apr,may,june,july,aug,sep,october,nov,dec)
    mes = bot.send_message(message.chat.id, 'Введите месяц рождения клиента на клавиатуре', reply_markup=markup)
    bot.register_next_step_handler(mes, date_month_answer)


def date_month_answer(message):
    user_id = str(message.chat.id)
    for i in range(len(month)):
        if message.text == month[i]:
            m = str(i + 1)
            if len(m) < 2:
                m = '0' + m
                info_client_dict[user_id].append(m)
            else:
                info_client_dict[user_id].append(m)
    mes = bot.send_message(message.chat.id, 'Введите дату рождения клиента')
    bot.register_next_step_handler(mes,date_birth)


def date_birth(message):
    user_id = str(message.chat.id)
    date = message.text
    if len(date) < 2:
        date = '0' + date
        info_client_dict[user_id].append(date)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        tlg = types.KeyboardButton('Телеграм')
        wa = types.KeyboardButton('WhatsApp')
        markup.add(tlg, wa)
        mes = bot.send_message(message.chat.id, 'Выберите,в каком мессенджере клиенту отправлять рассылку', reply_markup=markup)
        bot.register_next_step_handler(mes, app_client)
    elif len(date) > 2:
        mes = bot.send_message(message.chat.id, 'Введите корректную дату')
        bot.register_next_step_handler(mes, date_birth)
    else:
        info_client_dict[user_id].append(date)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        tlg = types.KeyboardButton('Телеграм')
        wa = types.KeyboardButton('WhatsApp')
        markup.add(tlg, wa)
        mes = bot.send_message(message.chat.id, 'Выберите,в каком мессенджере клиенту отправлять рассылку',
                               reply_markup=markup)
        bot.register_next_step_handler(mes, app_client)


def app_client(message):
    user_id = str(message.chat.id)
    if message.text == 'Телеграм':
        app = 'tlg'
        info_client_dict[user_id].append(app)
        check(message)
    elif message.text == 'WhatsApp':
        app = 'wa'
        info_client_dict[user_id].append(app)
        check(message)


def check(message):
    user_id = str(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Все верно')
    btn2 = types.KeyboardButton('Заполнить заново')
    markup.add(btn, btn2)
    mes = bot.send_message(message.chat.id, f"Проверьте правильность данных о клиенте: \n"
                                      f'Имя: {info_client_dict.get(user_id).__getitem__(0)} \n'
                                      f'Телефон: +7{info_client_dict.get(user_id).__getitem__(1)} \n'
                                      f'Дата рождения: {info_client_dict.get(user_id).__getitem__(3) + "." + info_client_dict.get(user_id).__getitem__(2)}', reply_markup=markup)
    bot.register_next_step_handler(mes, final_answer)


def final_answer(message):
    user_id = str(message.chat.id)
    if message.text == 'Все верно':
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM client_base WHERE chat_id = {user_id}")
            row = cursor.fetchone()
            pid = row.get('id')
        name_f = info_client_dict.get(user_id).__getitem__(0)
        phone_f = info_client_dict.get(user_id).__getitem__(1)
        date = '1980.' + info_client_dict.get(user_id).__getitem__(2) + "." + info_client_dict.get(user_id).__getitem__(3)
        app = info_client_dict.get(user_id).__getitem__(4)
        insert_info(pid, name_f, phone_f, date, app)
        info_client_dict.pop(user_id)
        bot.send_message(message.chat.id, 'Клиент успешно добавлен в базу')
        reset_info(message)
    elif message.text == 'Заполнить заново':
        info_client_dict.pop(user_id)
        answer_client(message)


def reset_info(message):
    if message.text == 'Все верно':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton('Да')
        btn2 = types.KeyboardButton('Нет, спасибо')
        markup.add(btn1, btn2)
        mes = bot.send_message(message.chat.id, 'Хотите добавить еще одного клиента?', reply_markup=markup)
        bot.register_next_step_handler(mes, answer_client)


def answer_sender(message):
    if message.text == 'Рассылка всем клиентам':
        mes = bot.send_message(message.chat.id, 'Введите текст рассылки. Учтите, что приветствие отправляется по умолчанию')
        bot.register_next_step_handler(mes, message_saver)
    elif message.text == 'Рассылка к д/р':
        bot.send_message(message.chat.id, 'Рассылка ко дню рождения происходит за 3 дня до конца текущего месяца. Тут вы можете задать текст, который будет отправлен вашим клиентам как поздравление или как предложение ко дню рождения.')
        mes = bot.send_message(message.chat.id, 'Введите текст рассылки. Учтите, что приветствие отправляется по умолчанию')
        bot.register_next_step_handler(mes, birth_mess_saver)


def birth_mess_saver(message):
    mess = str(message.text)
    user_id = str(message.chat.id)
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE client_base SET send_birth = '{mess}' WHERE chat_id = {user_id}")
        connection.commit()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton('Отлично')
    btn1 = types.KeyboardButton('Изменить')
    markup.add(btn, btn1)
    bot.send_message(message.chat.id, 'Отправляемое сообщение будет иметь следующий вид: \n'
                                      f'Здравствуйте, (имя клиента)! {mess}')
    mes = bot.send_message(message.chat.id, 'Как вам?', reply_markup=markup)
    bot.register_next_step_handler(mes, answer_birth)


def answer_birth(message):
    if message.text == 'Отлично':
        bot.send_message(message.chat.id, 'Я отправлю это сообщение вашим клиентам в конце месяца. Спасибо!')
        menu(message)
    elif message.text == 'Изменить':
        mes = bot.send_message(message.chat.id, 'Введите измененное сообщение')
        bot.register_next_step_handler(mes, birth_mess_saver)
    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Администратор", url='https://t.me/bublik_c_chaem')
        markup.add(btn)
        bot.send_message(message.chat.id, 'Обнаружена ошибка! Обратитесь к администратору.', reply_markup=markup)


def message_saver(message):
    user_id = str(message.chat.id)
    mess = str(message.text)
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE client_base SET send_all = '{mess}' WHERE chat_id = {user_id}")
        connection.commit()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton('Отправить')
    btn1 = types.KeyboardButton('Написать заново')
    markup.add(btn, btn1)
    bot.send_message(message.chat.id, 'Отправляемое сообщение будет иметь следующий вид: \n'
                                            f'Здравствуйте, (имя клиента)! {mess}' )
    mes = bot.send_message(message.chat.id, 'Отправить такое сообщение всем клиентам?', reply_markup=markup)
    bot.register_next_step_handler(mes, answerr)


def answerr(message):
    user_id = str(message.chat.id)
    if message.text == 'Отправить':
        sender_bot = telebot.TeleBot('5296562344:AAFRkKZdWqM8untSCYqyHjppB1bHsL9aNKM')
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT send_all FROM client_base WHERE chat_id = {user_id}")
            mess = cursor.fetchone()
            mess = mess.get('send_all')
            cursor.execute(f"SELECT id FROM client_base WHERE chat_id = {user_id}")
            id_sender = cursor.fetchone()
            id_sender = id_sender.get('id')
            cursor.execute(f"SELECT * FROM client_base WHERE pid = {id_sender} and deleted_at is null and chat_id is not null")
            adres = cursor.fetchall()
            for chat in adres:
                name_cli = chat.get('name')
                id_chat = chat.get('chat_id')
                sender_bot.send_message(id_chat, f'Здравствуйте, ' + name_cli + '! ' + mess)
            bot.send_message(message.chat.id, 'Рассылка завершена')
            menu(message)
    elif message.text == 'Написать заново':
        mes = bot.send_message(message.chat.id, 'Введите измененное сообщение')
        bot.register_next_step_handler(mes, message_saver)


bot.polling(non_stop=True)