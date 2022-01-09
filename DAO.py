from datetime import datetime

import mysql.connector

from Languages import Languages


class DAO:
    __cnx = mysql.connector.connect(user='root', password='1234',
                                    host='localhost', database='chatbot',
                                    auth_plugin='mysql_native_password')

    @staticmethod
    def create_new_user(user_id):
        cursor = DAO.__cnx.cursor()
        s = 'SELECT id_language FROM message_language WHERE name = \'en\''
        cursor.execute(s)
        default_lang_id = cursor.fetchone()[0]
        s = f'INSERT Chat VALUES ({user_id}, {default_lang_id}, NULL)'
        cursor.execute(s)
        DAO.__cnx.commit()
        s = f'INSERT Settings VALUES ({user_id}, TRUE ,TRUE ,TRUE ,TRUE ,TRUE ,TRUE)'
        cursor.execute(s)
        DAO.__cnx.commit()
        s = f'INSERT User_action VALUES ({user_id}, NULL)'
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def is_in_db(user_id):
        cursor = DAO.__cnx.cursor()
        s = f'SELECT * FROM Chat WHERE id_chat = {user_id}'
        cursor.execute(s)
        if not cursor.fetchone():
            return False
        return True

    @staticmethod
    def set_action(user_id, action_name):
        cursor = DAO.__cnx.cursor()
        if action_name:
            s = f'SELECT id_action FROM Actions WHERE action_description = \'{action_name}\''
            cursor.execute(s)
            id_action = cursor.fetchone()[0]
        else:
            id_action = "NULL"
        s = f"UPDATE User_action SET id_action = {id_action} WHERE id_chat = {user_id}"
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def get_action(user_id):
        cursor = DAO.__cnx.cursor()
        s = f"SELECT a.action_description FROM User_action u INNER JOIN Actions a " \
            f"ON u.id_action = a.id_action WHERE u.id_chat = {user_id}"
        cursor.execute(s)
        return cursor.fetchone()[0]

    @staticmethod
    def set_city(user_id, city_name):
        cursor = DAO.__cnx.cursor()
        s = f"UPDATE Chat SET city = \'{city_name}\' WHERE id_chat = {user_id}"
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def get_city(user_id):
        cursor = DAO.__cnx.cursor()
        s = f'SELECT city FROM Chat WHERE id_chat = {user_id}'
        cursor.execute(s)
        return cursor.fetchone()[0]

    @staticmethod
    def set_language(user_id, language):
        cursor = DAO.__cnx.cursor()
        s = f'SELECT id_language FROM Message_language WHERE name = \'{language}\''
        cursor.execute(s)
        id_language = cursor.fetchone()[0]

        s = f"UPDATE Chat SET id_language = {id_language} WHERE id_chat = {user_id}"
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def get_language(user_id):
        cursor = DAO.__cnx.cursor()
        s = f"SELECT m.name FROM Chat c INNER JOIN Message_language m " \
            f"ON c.id_language = m.id_language WHERE c.id_chat = {user_id}"
        cursor.execute(s)
        return cursor.fetchone()[0]

    @staticmethod
    def get_params(user_id):
        cursor = DAO.__cnx.cursor()
        s = f'SELECT humidity, temperature, feels_like_temperature, wind_speed, pressure, weather_description ' \
            f'FROM Settings WHERE id_chat = {user_id}'
        cursor.execute(s)
        return cursor.fetchone()

    @staticmethod
    def set_params(user_id, params):
        cursor = DAO.__cnx.cursor()
        s = f"UPDATE Settings SET humidity = {params[0]}, temperature = {params[1]}, " \
            f"feels_like_temperature = {params[2]}, wind_speed = {params[3]}, pressure = {params[4]}," \
            f" weather_description = {params[5]} WHERE id_chat = {user_id}"
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def create_subscription(user_id, time, lang):
        cursor = DAO.__cnx.cursor()
        s = f'select count(*) from subscription where id_chat ={user_id}'
        cursor.execute(s)
        count = cursor.fetchone()[0]
        if count >= 10:
            raise TypeError(Languages.get_message("dao_type_err", lang))
        s = f'select count(*) from subscription where id_chat ={user_id} and time_slot = \'{time}\''
        cursor.execute(s)
        count = cursor.fetchone()[0]
        if count != 0:
            raise ValueError(Languages.get_message("dao_value_err", lang))
        s = f'INSERT Subscription VALUES (0 , {user_id}, \'{time}\')'
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def del_subscription(user_id, time):
        cursor = DAO.__cnx.cursor()
        s = f'delete FROM chatbot.subscription where id_chat = {user_id} and time_slot = \'{time}\''
        cursor.execute(s)
        DAO.__cnx.commit()

    @staticmethod
    def get_subscriptions(user_id):
        cursor = DAO.__cnx.cursor()
        s = f'select time_slot from subscription where id_chat ={user_id}'
        cursor.execute(s)
        times = []
        for i in cursor.fetchall():
            t = str(i[0])
            times.append(t[:len(t)-3])
        return times.sort()

    @staticmethod
    def get_users_subscribe_for_time(time):
        cursor = DAO.__cnx.cursor()
        s = f'select id_chat from subscription where time_slot = \'{time}\''
        cursor.execute(s)
        t1 = cursor.fetchall()
        t2 = []
        for i in t1:
            t2.append(i[0])
        return t2

