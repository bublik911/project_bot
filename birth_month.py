import telebot
from connetion import connection
from datetime import datetime


with connection.cursor() as cursor:
    cursor.execute("SELECT id, send_birth, chat_id FROM client_base WHERE pid = 0")
    table_cons = cursor.fetchall()
    cursor.execute('select MONTH(DATE_ADD(curdate(), INTERVAL 1 MONTH))')
    month_now = list(cursor.fetchone().values())[0]
    for i in range(len(table_cons)):
        k = 0
        finish = 'Рассылка произведена успешно: \n'
        sender_chat_id = table_cons[i].get('chat_id')
        id_sender = table_cons[i].get('id')
        message_sender = table_cons[i].get('send_birth')
        cursor.execute(f"SELECT name, chat_id, date, phone FROM client_base WHERE pid = {id_sender} and deleted_at is NULL and chat_id is not NULL")
        table_clients = cursor.fetchall()
        for i in range(len(table_clients)):
            name_cli = str(table_clients[i].get('name'))
            chat_id_cli = table_clients[i].get('chat_id')
            phone_cli = '+7' + table_clients[i].get('phone')
            date_cli = int(str(table_clients[i].get('date')).split('-')[1])
            if date_cli == month_now:
                time = datetime.now().strftime('%H:%M')
                k += 1
                sender_bot = telebot.TeleBot('5296562344:AAFRkKZdWqM8untSCYqyHjppB1bHsL9aNKM')
                sender_bot.send_message(chat_id_cli, 'Здравствуйте, ' + name_cli + '!' + message_sender)
                finish += str(k) + ') ' + name_cli +' ' + time + '\n' + phone_cli + '\n'
        fin_bot = telebot.TeleBot('5408757344:AAFGtHco9x9xdezFeadsV6aGe7rPAjijRqg')
        fin_bot.send_message(sender_chat_id, finish)