import requests
import telebot
from telebot import types
import logging
import sqlite3
from database import save_user_data, get_user_data, update_user_data
TOKEN = '6844197077:AAGeJhe0rM7F5diwJgbGo95u5IgyVYO0mSs'
bot = telebot.TeleBot(TOKEN)
conn = sqlite3.connect('users_data.db',check_same_thread=False)
conn.commit()
users = {}

URL = 'http://localhost:1234/v1/chat/completions'
HEADERS = {"Content-Type": "application/json"}

MAX_TOKENS = 1024
assistant_content = ""
question = ""
system_content = ""


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'send_content':
        send_content(call.message)
    elif call.data == 'continue_conversation':
        continue_conversation(call.message)
    elif call.data == 'end':
        end(call.message)

def make_promt(message):
    user_id = message.chat.id
    system_content, question, assistant_content = get_user_data(conn,user_id)
    json = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},

        ],
        "temperature": 1.5,
        "max_tokens": 1024,
    }
    return json

def make_conpromt(message):
    user_id = message.chat.id
    system_content, question, assistant_content = get_user_data(conn,user_id)
    json = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
            {"role": "assistant", "content": assistant_content},
        ],
        "temperature": 1.5,
        "max_tokens": 1024,
    }
    return json

def process_resp(response,message):
    full_response = response
    try:
        resp_json = response.json()
        messages = resp_json["choices"][0]["message"]["content"]
        user_id = message.chat.id
        system_content, question, assistant_content = get_user_data(conn,user_id)
        assistant_content += messages
        update_user_data(conn,user_id, system_content, question, assistant_content)
        if messages != "":
            bot.send_message(message.chat.id,f"Ответ GPT: {messages}")
        else:
            bot.send_message(message.chat.id, f"Я не знаю как ответить")
        start(message)
    except Exception as e:
        bot.send_message(message.chat.id,f"Произошла ошибка при обработке ответа: {e}")
    return full_response

def send_content(message):
    bot.send_message(message.chat.id,"Напишите предмет для объяснения")
    bot.register_next_step_handler(message, add_user)

def add_user(message):
    system_content = ""
    system_content += f"Ты объясняешь предмет - {message.text}."
    print(system_content)
    bot.send_message(message.chat.id, "Напишите сложность для объяснения(однокласник, учитель, профессор)")
    bot.register_next_step_handler(message, add_user1, system_content)


def add_user1(message,system_content):
    system_content += f"Ты объяснеящь как {message.text}"
    print(system_content)
    user_id = message.chat.id
    print(user_id)
    save_user_data(conn,user_id,system_content,"","")
    send_request(message)
def send_request(message):
    bot.send_message(message.chat.id, "Напишите задачу для GPT")
    bot.register_next_step_handler(message, messageofuser)

def messageofuser(message):
    user_id = message.chat.id
    print(user_id)
    system_content, question, assistant_content = get_user_data(conn,user_id)
    user_request = message.text
    question = user_request
    print(user_id)
    update_user_data(conn,user_id, system_content, question, assistant_content)
    prompt = make_promt(message)
    try:
        response = requests.post(URL, json=prompt, headers=HEADERS)
        if response.status_code == 200:
            process_resp(response, message)
        else:
            bot.send_message(message.chat.id, "Произошла ошибка при отправке запроса. Попробуйте снова.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при отправке запроса: {e}")

def continue_conversation(message):
    prompt = make_conpromt(message)
    try:
        response = requests.post(URL, json=prompt, headers=HEADERS)
        if response.status_code == 200:
            process_resp(response,message)
        else:
            bot.send_message(message.chat.id,"Произошла ошибка при отправке запроса. Попробуйте снова.")
    except Exception as e:
        bot.send_message(message.chat.id,f"Произошла ошибка при отправке запроса: {e}")

def end(message):
    bot.send_message(message.chat.id,"До новых встреч!")
    exit(0)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Запрос к GPT', callback_data='send_content'))
    keyboard.add(types.InlineKeyboardButton(text='Продолжить ответ', callback_data='continue_conversation'))
    keyboard.add(types.InlineKeyboardButton(text='Выход', callback_data='end'))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


if __name__ == "__main__":
    bot.polling()