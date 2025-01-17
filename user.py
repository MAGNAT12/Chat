import json
import requests
import sqlite3
import secrets
import string

connect = sqlite3.connect('user.db', check_same_thread=False) 
cursor = connect.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        token TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS send_message(
        name TEXT,
        messages TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS get_message(
        name TEXT,
        messages TEXT
    )
""")

connect.commit()

headers = {'Content-Type': 'application/json'}

def register(name, gmail, password):
    data = {
        "name": name,
        "gmail": gmail,
        "password": password,
    }
    response = requests.post("http://127.0.0.1:3000/api/regist", data=json.dumps(data), headers=headers)
    a = response.json()
    print(a['message'])

def profil(name, gmail, password):
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(10))
    cursor.execute("SELECT name FROM users WHERE token = ?", (token,))
    data = cursor.fetchone()
    if data is None:
        cursor.execute("INSERT INTO users(name, token) VALUES (?, ?)", (name, token))
        connect.commit()
    else:
        pass
    data = {
        "name": name,
        "gmail": gmail,
        "password": password,
        "token": token
    }
    response = requests.post("http://127.0.0.1:3000/api/user", data=json.dumps(data), headers=headers)
    a = response.json()
    print(a['message'])

def message(name, messages):
    cursor.execute("SELECT name FROM users")
    name_sender = cursor.fetchall()
    cursor.execute("SELECT token FROM users")
    token = cursor.fetchall()
    date = {
        "name_sender":name_sender,
        "name":name,
        "message":messages,
        "token": token
    }
    respons = requests.post("http://127.0.0.1:3000/api/send_message", data=json.dumps(date), headers=headers)
    if respons.status_code == 200:
        cursor.execute("INSERT INTO send_message(name, messages) VALUES (?, ?)", (name, messages))
        connect.commit()
        print("Сообщение отправелено")
    else:
        print(f"Ошибка: {respons.json()}")

def get():
    cursor.execute("SELECT token FROM users")
    token = cursor.fetchone()  
    if token:
        token = token[0]
    else:
        print("Токен не найден!")
        return

    date = {
        "token": token
    }
    respons = requests.get("http://127.0.0.1:3000/api/get_messages", data=json.dumps(date), headers=headers)

    if respons.status_code == 200:
        a = respons.json()
        print(a['name_sender'],":",a['message'])

def search():
    data = {
        "name":"asd"
    }
    res = requests.post("http://127.0.0.1:3000/api/search",params=data)
    print(res.json)

def send_all_message():
    cursor.execute("SELECT * FROM send_message")
    messages = cursor.fetchall()
    for message in messages:
        print(f"name: {message[0]}, message:{message[1]}")

def get_all_messages():
    cursor.execute("SELECT * FROM get_message")
    messages = cursor.fetchall()
    for message in messages:
        print(f"name: {message[0]} message:{message[1]},")

if __name__ == "__main__":
    token = None
    while True:
        print("1. Зарегистрироваться")
        print("2. Вход")
        print("3. Отправить сообщение")
        print("4. Для получения сообщений")
        print("5. Посмотреть все отправленные сообщения")
        print("6. Посмотреть все полученные сообщения")
        print("7. Выход")
        choice = input("Выберите: ")
        if choice == "1":
            name = input("Введите имя: ")
            gmail = input("Введите gmail: ")
            password = input("Введите пароль: ")
            register(name, gmail, password)
            print("---------------")
        elif choice == "2":
            name = input("Введите имя: ")
            gmail = input("Введите gmail: ")
            password = input("Введите пароль: ")
            profil(name, gmail, password)
            print("---------------")
        elif choice == "3":
            recipient_name = input("Введите имя кому хотите отправить сообщение: ")
            message_text = input("Введите сообщение которое хотите отправить: ")
            message(recipient_name, message_text)
            print("---------------")
        elif choice == "4":
            get()
            print("---------------")
        elif choice == "5":
            send_all_message()
            print("---------------")
        elif choice == "6":
            get_all_messages()
            print("---------------")
        elif choice == "7":
            break

