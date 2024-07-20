from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
import sqlite3
import threading
import time
import hashlib
import os

app = Flask(__name__)
api = Api(app)

connect = sqlite3.connect('Chat.db', check_same_thread=False)
cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS 
            users(
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL,
               gmail TEXT NOT NULL,
               password TEXT NOT NULL
            )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS
               mes(
               name_sender TEXT NOT NULL,
               name TEXT NOT NULL,
               message TEXT NOT NULL,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS
               ton(
               name TEXT NOT NULL,
               token TEXT NOT NULL
               )""")

cursor.execute('PRAGMA journal_mode = OFF')
connect.commit()


journal_file = 'Chat.db-journal'

if os.path.exists(journal_file):
    os.remove(journal_file)

class Name_gmail(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument('gmail', type=str)
        parser.add_argument('password', type=str)
        args = parser.parse_args()
        name = args["name"]
        gmail = args['gmail']
        cursor.execute(f"SELECT `name`, `gmail` FROM `users` WHERE `name` = '{name}' AND `gmail` = '{gmail}'")
        data = cursor.fetchone()
        if data is None:
            name = args["name"]
            gmail = args['gmail']
            password = args['password']
            password_ha = hashlib.sha3_512(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (name, gmail, password) VALUES (?, ?, ?);", (name, gmail, password_ha))
            connect.commit()
            return {'message': 'Вы зарегистрированны'}, 200
        else:
            return {'message': 'Ник уже зарегистрированн'}, 400
        
class Send_message(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name_sender", type=str)
        parser.add_argument("name", type=str)
        parser.add_argument("message", type=str)
        parser.add_argument("token", type=str)
        args = parser.parse_args()
        name_sender = args["name_sender"]
        name = args['name']
        message = args['message']
        token = args['token']
        cursor.execute("SELECT name FROM users WHERE `name` = ?", (name,))
        data = cursor.fetchone()
        if data:
            cursor.execute("SELECT token FROM ton WHERE `token` = ?", (token,))
            data = cursor.fetchone()
            if data is None:
                cursor.execute("INSERT INTO mes(name_sender, name, message) VALUES (?, ?, ?);", (name_sender, name, message))
                connect.commit()
                connect.close()
                return {'message': 'сообщение отправлено'}
            else:
                return {"message":"Вы не вошли в профель"}
        else:
            return {'message': "НЕ найде пользователь"}


class Get_messages(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name_devices", type=str)
        args = parser.parse_args()
        name_devices = args['name_devices']
        cursor.execute(f"SELECT `name_devices` FROM devices WHERE `name_devices` = '{name_devices}'")
        data = cursor.fetchone()
        if data:
            cursor.execute('SELECT name FROM devices WHERE `name_devices` = ?', (name_devices,))
            name_sender = cursor.fetchone()
            name_sender = name_sender[0]
            cursor.execute("SELECT name_sender, message, timestamp FROM mes WHERE name = ?", (name_sender,))
            messages = cursor.fetchall()
            if messages:
                messages_list = [{'name_sender': msg[0], 'message': msg[1]} for msg in messages]
                return jsonify(messages_list)
            else:
                return {'message': 'Сообщений не найдено'}
        else:
            connect.close()
            return {"message": "Зарегистрируйтесь"}

        
class Profil_user(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument('gmail', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument("token", type=str)
        args = parser.parse_args()
        name = args["name"]
        gmail = args["gmail"]
        password = args['password']
        token = args['token']
        password_ha = hashlib.sha3_512(password.encode()).hexdigest()
        cursor.execute("SELECT name, gmail, password FROM users WHERE name = ? AND gmail = ? AND password = ?", (name, gmail, password_ha))
        data = cursor.fetchall()
        data_str = str(data)
        if  name in data_str:
            cursor.execute("SELECT name FROM ton WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data is None:
                cursor.execute('INSERT INTO ton (token, name) VALUES (?, ?)', (token, name))
                connect.commit()
                return {"message": "Вы вошли в профиль"}
            else:
                return {"message": "Вы уже вошли в профиль"}
        else:
            return {"message": "Зарегистрируйтесь"}


api.add_resource(Name_gmail, "/api/regist")
api.add_resource(Send_message, "/api/send_message")
api.add_resource(Get_messages, "/api/get_messages")
api.add_resource(Profil_user, "/api/user")

def delete_old_messages():
    while True:
        cursor.execute("DELETE FROM mes WHERE timestamp <= datetime('now', '-1 hours')")
        connect.commit()
        time.sleep(3600)

thread = threading.Thread(target=delete_old_messages, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="127.0.0.1")
