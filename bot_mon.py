import requests
import pymysql
import datetime
import time

token = 'my_token'
url = 'https://api.telegram.org/bot' + token + '/'


#ДОБАВЛЕНИЕ ID ЧАТА В БАЗУ ДАННЫХ
def add_user(chat_id):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='bot_mon',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            try:
                sql = "INSERT INTO `users` (`chat_id`) VALUE (%s)"
                cursor.execute(sql, (chat_id))
            except:
                pass
        connection.commit()
    finally:
        connection.close()


#ДАННАЯ ФУНКЦИЯ ПЕРЕВОДИТ ДЕЖУРСТВО НА ПОЛЬЗОВАТЕЛЯ ОТПРАВИВШЕГО СООБЩЕНИЕ - '/take_duty'
def take_duty(chat_id):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='bot_mon',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            try:
                sql1 = "UPDATE `duty` SET `end_time` = %s WHERE 'id' = (SELECT max(id) FROM 'duty')"
                sql2 = "INSERT INTO `duty` (`chat_id`, `start_time`, `end_time`) VALUE (%s, %s, %s)"
                cursor.execute(sql1, (datetime.datetime.now()))
                cursor.execute(sql2, (chat_id, datetime.datetime.now(), datetime.datetime.now()))
            except:
                pass
        connection.commit()
    finally:
        connection.close()


#ДАННАЯ ФУНКЦИЯ ВЫВОДИТ, КТО В ДАННЫЙ МОМЕНТ НАХОДИТСЯ НА ДЕЖУРСТВЕ
def who_is_on_duty():
    result = ''
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='bot_mon',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            try:
                sql = "SELECT a.name \
                        FROM 'users' AS a \
                        JOIN 'duty' AS c ON a.chat_id = c.chat_id \
                        WHERE c.chat_id = ( \
                        	SELECT chat_id \
                            FROM 'duty' \
                            WHERE id = ( \
                        		SELECT max(id) \
                                FROM 'duty' \
                                ) \
                        	)"
                cursor.execute(sql, (chat_id,))
                result = cursor.fetchone()
            except:
                pass
        connection.commit()
    finally:
        connection.close()
    return(result)


#ФУНКЦИЯ, ВЫПОЛНЯЮЩАЯ ОПЕРАЦИЮ ВЗЯТИЯ И СНЯТИЯ ИНЦИДЕНТА ИНЖЕНЕРОМ
def take_drop_incident(id, chat_id, str):



#ФУНКЦИЯ ОТЧИЩЕНИЯ СЛОВАРЯ ОТ СТАРЫХ СООБЩЕНИЙ
def del_mess(update_id):
    method = url + 'getupdates'
    check = False
    if str == 'take':
        sql = "UPDATE 'incident' SET ack=%s WHERE id=%s"
    else:
        sql = "UPDATE 'incident' SET ack='' WHERE id=%s"
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='bot_mon',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql, (chat_id, id))
                check = True
            except:
                pass
        connection.commit()
    finally:
        connection.close()
    if check:
        if str == 'take':
            return 'Вы взяли инцидент #' + id
        else:
            return 'Вы сняли инцидент #' + id
    else:
        return 'Произошла ошибка, команда не выполнена!'


#ФУНКЦИЯ, ДОБАВЛЯЮЩАЯ В БАЗУ ДАННЫХ ОТЧЕТ О ПРОДЕЛАННОЙ РАБОТЕ ПО УСТРАНЕНИЮ ИНЦИДЕНТА
def write_postmortem(id, chat_id, postmortem):
    check = False
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='bot_mon',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            try:
                sql = "INSERT INTO `postmortems` (`incident_id`, `chat_id`, `text`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (id, chat_id, postmortem))
                check = True
            except:
                pass
        connection.commit()
    finally:
        connection.close()
    if check:
        return 'Отчет успешно добавлен в базу!'
    else:
        return 'Произошла ошибка, команда не выполнена!'


#ФУНКЦИЯ ВОЗВРАЩАЮЩАЯ СЛОВАРЬ С НОВЫМИ СООБЩЕНИЯМИ
def get_updates(url):
    method = url + 'getUpdates'
    r = requests.get(method)
    data = r.json()
    return data['result']


#ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЮ
def send_message(chat_id, message):
    method = url + 'sendMessage'
    r = requests.get(method, params={'chat_id': chat_id, 'text': message})


#ОСНОВНАЯ ЧАСТЬ ПРОГРАММЫ, В КОТОРОЙ ПРОИСХОДИТ ВЫЗОВ ФУНКЦИЙ
if __name__ == '__main__':
    print('BOT IS WORKING...')
    while True:
        time.sleep(1)
        data = get_updates(url)
        for e in data:
            message = e['message']['text']
            update_id = e['update_id']
            chat_id = e['message']['chat']['id']

            if message == '/start':
                text = 'Hi, gay! \n/who_is_on_duty\n/take_duty\n/take_incident [id_of_the_incident]\n \
                        /drop_incident [id_of_the_incident]\n/postmortem [id_of_the_incident] [your_postmortem]'
                add_user(chat_id)
                send_message(chat_id, text)

            elif message == '/take_duty':
                take_duty(chat_id)
                text = who_is_on_duty() + ' is on duty right now!'
                send_message(chat_id, text)

            elif message == '/who_is_on_duty':
                text = who_is_on_duty() + ' is on duty right now!'
                send_message(chat_id, text)

            elif message[0:14] == '/take_incident':
                id = message[15:len(message)]
                print(id)
                text = take_drop_incident(id, chat_id, 'take')
                send_message(chat_id, text)

            elif message[0:14] == '/drop_incident':
                id = message[15:len(message)]
                print(id)
                text = take_drop_incident(id, chat_id, 'drop')
                send_message(chat_id, text)

            elif message[0:11] == '/postmortem':
                a = message.find(' ', [12],[len(message)])
                id = message[12:a + 1]
                postmortem = message[a + 1:len(message)]
                print(id)
                text = write_postmortem(id, chat_id, postmortem)
                send_message(chat_id, text)


        del_mess(update_id)
