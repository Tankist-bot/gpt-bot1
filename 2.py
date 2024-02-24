import requests
import telebot
from telebot import types
import logging

TOKEN = '6844197077:AAGeJhe0rM7F5diwJgbGo95u5IgyVYO0mSs'
bot = telebot.TeleBot(TOKEN)

users = {}

URL = 'http://localhost:1234/v1/chat/completions'
HEADERS = {"Content-Type": "application/json"}

MAX_TOKENS = 1024
assistant_content = ""
question = ""
system_content = "Ты танкист. Тебя зовут Вася Пупкин. Отвечай на вопросы как будто ты кантужен."


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
    if call.data == 'send_request':
        send_request(call.message)
    elif call.data == 'continue_conversation':
        continue_conversation(call.message)
    elif call.data == 'end':
        end(call.message)

def make_promt(user_request):
    json = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_request},

        ],
        "temperature": 1.5,
        "max_tokens": 1024,
    }
    return json

def make_conpromt(user_request):
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
    global assistant_content, users
    full_response = response
    try:
        resp_json = response.json()
        messages = resp_json["choices"][0]["message"]["content"]
        assistant_content += messages
        if messages != "":
            bot.send_message(message.chat.id,f"Ответ GPT: {messages}")
        else:
            bot.send_message(message.chat.id, f"Я не знаю как ответить")
        start(message)
    except Exception as e:
        bot.send_message(message.chat.id,f"Произошла ошибка при обработке ответа: {e}")
    return full_response

def send_request(message):
    global assistant_content, question, users
    user_id = message.chat.id
    assistant_content = ""
    question = ""
    sp = [assistant_content,question]
    if user_id in users:
        users[user_id] = sp
        print(users,22222)
    else:
        users.update({user_id: sp})
        print(users,11111)
    assistant_content = ""
    bot.send_message(message.chat.id, "Напишите запрос")
    @bot.message_handler(func=lambda message: True)
    def handle_user_request(message):
        global assistant_content, question, users
        user_id = message.chat.id
        sp = users.get(user_id)
        assistant_content = sp[0]
        question = sp[1]
        user_request = message.text
        question = user_request
        sp = [assistant_content,question]
        users[user_id] = sp
        prompt = make_promt(user_request)
        try:
            response = requests.post(URL, json=prompt, headers=HEADERS)
            if response.status_code == 200:
                process_resp(response,message)
            else:
                bot.send_message(message.chat.id,"Произошла ошибка при отправке запроса. Попробуйте снова.")
        except Exception as e:
            bot.send_message(message.chat.id,f"Произошла ошибка при отправке запроса: {e}")

    bot.register_next_step_handler(message, handle_user_request)

def continue_conversation(message):
    global assistant_content, users
    prompt = make_conpromt(assistant_content)
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
    keyboard.add(types.InlineKeyboardButton(text='Запрос к GPT', callback_data='send_request'))
    keyboard.add(types.InlineKeyboardButton(text='Продолжить ответ', callback_data='continue_conversation'))
    keyboard.add(types.InlineKeyboardButton(text='Выход', callback_data='end'))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


if __name__ == "__main__":
    bot.polling()