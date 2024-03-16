
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN, MAX_TOKENS

bot = TeleBot(TOKEN)
MAX_LETTERS = MAX_TOKENS

'''
Добро пожаловать в "TeamWork" 
Выполняй небольшие задачи ниже и получай баллы!
Максимальное количество баллов: 18

P.S. Некоторые задачи связаны, и их можно выполнить только при выполнении предыдущей
'''

# Словарик для хранения задач пользователей и ответов GPT
users_history = {}


# Функция для создания клавиатуры с нужными кнопочками
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


# Приветственное сообщение /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник для решения разных задач!\n"
                          f"Ты можешь прислать условие задачи, а я постараюсь её решить.\n"
                          "Иногда ответы получаются слишком длинными - в этом случае ты можешь попросить продолжить.",
                     reply_markup=create_keyboard(["/solve_task", '/help']))


# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text="Чтобы приступить к решению задачи: нажми /solve_task, а затем напиши условие задачи",
                     reply_markup=create_keyboard(["/solve_task"]))


# Команда /solve_task и регистрация функции get_promt() для обработки любого следующего сообщения от пользователя



@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    bot.send_message(message.chat.id, "Напиши условие новой задачи:")
    bot.register_next_step_handler(message, get_promt)


# Фильтр для обработки кнопочки "Продолжить решение"
def continue_filter(message):
    button_text = 'Продолжить решение'
    return message.text == button_text


# Получение задачи от пользователя или продолжение решения
@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = message.from_user.id

    if not message.text:
        bot.send_message(user_id, "Необходимо отправить именно текстовое сообщение")
        bot.register_next_step_handler(message, get_promt)
        return

    # Получаем текст сообщения от пользователя
    user_request = message.text


    if len(user_request) > MAX_LETTERS:
        bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, get_promt)
        return


    if user_id not in users_history:
        # Сохраняем промт пользователя и начало ответа GPT в словарик users_history
        users_history[user_id] = {
            'system_content': "Ты - дружелюбный помощник для решения задач по математике. Давай подробный ответ с решением на русском языке",
            'user_content': user_request,
            'assistant_content': "Решим задачу по шагам: "
        }

    # Пока что ответом от GPT будет любой текст, просто придумай его)
    answer = "Позже здесь будет реальное решение, а пока что так :)"

    users_history[user_id]['assistant_content'] += answer + '\n'

    bot.send_message(user_id, users_history[user_id]['assistant_content'], reply_markup=create_keyboard(['Продолжить решение', 'Завершить решение']))
    if user_id not in users_history:
        bot.send_message(user_id, "Для начала решения задачи, напиши /solve_task")
        return
    if not users_history[user_id].get('system_content'):
        bot.send_message(user_id, "Сначала начни задачу, прежде чем продолжить")
        bot.register_next_step_handler(message, get_promt)
        return





def end_filter(message):
    button_text = 'Завершить решение'
    return message.text == button_text


@bot.message_handler(content_types=['text'], func=end_filter)
def end_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Текущие решение завершено")
    users_history[user_id] = {}
    solve_task(message)
    if not users_history[user_id].get('system_content'):
        bot.send_message(user_id, "Сначала начни задачу, прежде чем продолжить")
        bot.register_next_step_handler(message, get_promt)
        return


'''
Добавь в функции get_promt и end_task проверку состояния пользователя.
Например, если пользователь не начал диалог, но хочет продолжить ответ - бот отправит сообщение об ошибке и предложит сначала начать задачу

За выполнение: 3 балла
'''


bot.polling()
