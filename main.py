import telebot
import random
import MYToken
from telebot import types
import re

bot = telebot.TeleBot(MYToken.TOKEN)

games = {}


# ініціалізація нової ігрової дошки
def create_board():
    return [[" " for _ in range(3)] for _ in range(3)]


# перевірка, чи виграв гравець у грі
def check_winner(board, player):
    for row in board:
        if all([cell == player for cell in row]):
            return True
    for col in range(3):
        if all([board[row][col] == player for row in range(3)]):
            return True
    if all([board[i][i] == player for i in range(3)]) or all([board[i][2 - i] == player for i in range(3)]):
        return True
    return False

# перевірка, чи заповнена вся ігрова дошка
def is_board_full(board):
    return all([cell != " " for row in board for cell in row])


# оновлення ігрового поля
def render_board(board):
    return "\n".join([" | ".join(row) for row in board])


# command "statr"
@bot.message_handler(commands=['StartRaiden'])
def welcome(message):
    sti = open('1.webm', 'rb')
    bot.send_sticker(message.chat.id, sti)
    sti.close()

    bot.send_message(message.chat.id,
                     f"Ласкаво просимо, {message.from_user.first_name}!\nЯ - {bot.get_me().first_name}, бот, створений для експериментів.",
                     parse_mode='html')


# Цікаво? ні!
@bot.message_handler(
    func=lambda message: message.text.lower() in ["тобі цікаво?", "Тобі цікаво?", "тобі цікаво", "Тобі цікаво"])
def zaprograming(message):
    bot.send_message(message.chat.id, "Ні, я так запрограмований.")


# шо?
@bot.message_handler(func=lambda message: message.text.lower() in ["шо?", "що?", "что?", "как?"])
def whate(message):
    sti = open('what.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    sti.close()


# Призив демона
@bot.message_handler(func=lambda message: message.text.lower() in ["Райден", "РАЙДЕН", "райден"])
def jack_response(message):
    markup = types.InlineKeyboardMarkup(row_width=2)

    item1 = types.InlineKeyboardButton("😊 Як справи?", callback_data='how_are_you')
    item2 = types.InlineKeyboardButton("❌⭕️ Хрестики-Нолики", callback_data='tic_tac_toe')
    item3 = types.InlineKeyboardButton("🎲 Вгадай число", callback_data='guess_the_number')
    item4 = types.InlineKeyboardButton("🩸 Кров", callback_data='Blood')
    item5 = types.InlineKeyboardButton("👨🏽‍💻 Зв'язок з недопрограмістом", callback_data='admine')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id, "Шо надо?", reply_markup=markup)


# Обробка повідомлення з рандомними числами
@bot.message_handler(func=lambda message: re.match(r'рандом', message.text.lower()))
def random_number(message):
    # Перевірка на наявність діапазону у форматі "рандом від (число) до (число)"
    range_match = re.search(r'від (\d+) до (\d+)', message.text.lower())

    if range_match:
        # Якщо діапазон вказаний, генеруємо число в цьому діапазоні
        low = int(range_match.group(1))
        high = int(range_match.group(2))
        if low > high:
            bot.send_message(message.chat.id, "Помилка: мінімальне значення більше за максимальне.")
        else:
            random_num = random.randint(low, high)
            bot.send_message(message.chat.id, f"Випадкове число в діапазоні від {low} до {high}: {random_num}")
    else:
        # Якщо діапазон не вказаний, генеруємо число від -1000 до 1000
        random_num = random.randint(-1000, 1000)
        bot.send_message(message.chat.id, f"Випадкове число: {random_num}")


# Вгадай число
# Генерація випадкового числа
def generate_random_number():
    random_number = random.sample(range(10), 4)
    return ''.join(map(str, random_number))


# Перевірка введеного числа користувача
def check_user_input(user_input, random_number):
    if user_input == random_number:
        return "UGADAL!!!"

    correct_place = sum(1 for i in range(4) if user_input[i] == random_number[i])
    correct_number = sum(1 for c in user_input if c in random_number) - correct_place

    if correct_place > 0:
        return f"Вгадано {correct_place} цифру(и)"
    elif correct_number > 0:
        return "Мимо"
    else:
        return "Миимоо"


# Обробка команди для початку гри
@bot.message_handler(commands=['start_game'])
def start_game(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton("🎲 Грати в гру 'Вгадай число'", callback_data='guess_the_number')
    item2 = types.InlineKeyboardButton("🎲 Грати в гру 'Хрестики-Нолики'", callback_data='tic_tac_toe')

    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Виберіть гру:", reply_markup=markup)


# Обробка натискання кнопки для початку гри
@bot.callback_query_handler(func=lambda call: call.data == 'guess_the_number')
def guess_the_number(call):
    chat_id = call.message.chat.id
    games[chat_id] = {"random_number": generate_random_number(), "players": {}}
    bot.send_message(chat_id, "Я загадав число. Спробуйте його вгадати, вводячи 4 цифри без повторів.")


# Обробка вводу чисел від користувача
@bot.message_handler(
    func=lambda message: len(message.text) == 4 and message.text.isdigit() and len(set(message.text)) == 4)
def handle_guess(message):
    chat_id = message.chat.id
    game = games.get(chat_id)

    if not game:
        bot.send_message(chat_id, "Гра не розпочата. Використовуйте /start_game для початку гри.")
        return

    user_input = message.text
    random_number = game["random_number"]
    result = check_user_input(user_input, random_number)

    if result == "UGADAL!!!":
        bot.send_message(chat_id, f"Вітаю! Ви вгадали число: {random_number}")
        del games[chat_id]  # Завершення гри
    else:
        bot.send_message(chat_id, result)


# кров
# Стани для трекінгу
USER_STATES = {}
USER_DATA = {}


# Обробка callback запитів
@bot.callback_query_handler(func=lambda call: call.data == 'Blood')
def handle_Blood(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id  # ID користувача, який ініціював запит
    user_name = call.from_user.username  # Ім'я користувача

    USER_STATES[chat_id] = 'enter_do'
    USER_DATA[chat_id] = {'user_id': user_id, 'user_name': user_name}
    bot.send_message(chat_id, "Введіть кількість крові до завдання:")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in USER_STATES:
        return

    state = USER_STATES[chat_id]

    if state == 'enter_do':
        try:
            do = int(message.text)
            USER_DATA[chat_id]['do'] = do
            USER_STATES[chat_id] = 'enter_pislya'
            bot.send_message(chat_id, "Введіть кількість крові після завдання:")
        except ValueError:
            bot.send_message(chat_id, "Помилка: Будь ласка, введіть число.")

    elif state == 'enter_pislya':
        try:
            pislya = int(message.text)
            do = USER_DATA[chat_id].get('do', 0)  # Получаем значение 'do' из USER_DATA
            blood = pislya - do
            USER_DATA[chat_id]['blood'] = blood
            USER_STATES[chat_id] = 'enter_res'
            bot.send_message(chat_id, "Ресурси твої? (так, ні)")
        except ValueError:
            bot.send_message(chat_id, "Помилка: Будь ласка, введіть число.")

    elif state == 'enter_res':
        res = message.text.lower()
        blood = USER_DATA[chat_id].get('blood', 0)  # Получаем значение 'blood' из USER_DATA
        user_id = USER_DATA[chat_id].get('user_id')
        user_name = USER_DATA[chat_id].get('user_name')

        if res == "ні":
            bot.send_message(chat_id, f"@{user_name} віддай {blood} крові та муні отримані зі завдання @tory_45")
            bot.send_message(chat_id, f"І про талісман не забудь!")
        elif res == "так":
            blood = blood / 2
            bot.send_message(chat_id, f"@{user_name} віддай {blood} крові @tory_45")
            bot.send_message(chat_id, f"І про талісман не забудь!")
        else:
            bot.send_message(chat_id, "Невірний вибір. Введіть 'так' або 'ні'.")
            return

        # Завершення обробки
        del USER_STATES[chat_id]
        del USER_DATA[chat_id]


# Зв'язок з недопрограмістом
@bot.callback_query_handler(func=lambda call: call.data == 'admine')
def admin(call):
    bot.send_message(call.message.chat.id, f"@Prosto_J_E_K_A")


# Як справи?
@bot.callback_query_handler(func=lambda call: call.data == 'how_are_you')
def how_are_you(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Добре", callback_data='good')
    item2 = types.InlineKeyboardButton("Не дуже", callback_data='bad')
    markup.add(item1, item2)
    bot.send_message(call.message.chat.id, 'Чудово, а ти як?', reply_markup=markup)


# Обробник відповіді "Добре"
@bot.callback_query_handler(func=lambda call: call.data == 'good')
def good_response(call):
    user_name = call.from_user.first_name
    bot.send_message(call.message.chat.id, f'{user_name} це добре що добре 😊')


# Обробник відповіді "Не дуже"
@bot.callback_query_handler(func=lambda call: call.data == 'bad')
def bad_response(call):
    user_name = call.from_user.first_name
    bot.send_message(call.message.chat.id, f'{user_name} ну не сумуй 😢')


# Хрестики-Нолики
@bot.callback_query_handler(func=lambda call: call.data == 'tic_tac_toe')
def tic_tac_toe(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Грати з ботом", callback_data='play_with_bot')
    item2 = types.InlineKeyboardButton("Грати з другом", callback_data='play_with_friend')
    markup.add(item1, item2)
    bot.send_message(call.message.chat.id, 'Виберіть, з ким грати:', reply_markup=markup)


# Хрестики-Нолики з ботом
@bot.callback_query_handler(func=lambda call: call.data == 'play_with_bot')
def play_with_bot(call):
    chat_id = call.message.chat.id
    games[chat_id] = {"board": create_board(), "player": "X", "mode": "bot",
                      "players": {"X": call.from_user.first_name, "O": "Бот"}, "turn": "X"}
    bot.send_message(chat_id,
                     f"Ви граєте за X проти Бота.\n{games[chat_id]['players']['X']} vs {games[chat_id]['players']['O']}\nВаш хід!",
                     reply_markup=generate_markup(chat_id))


# Хрестики-Нолики з другом
@bot.callback_query_handler(func=lambda call: call.data == 'play_with_friend')
def play_with_friend(call):
    chat_id = call.message.chat.id
    games[chat_id] = {"board": create_board(), "players": {"X": call.from_user.first_name, "O": None}, "turn": "X",
                      "mode": "player"}
    join_markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton("Приєднатися до гри", callback_data="join_game")
    join_markup.add(join_button)
    bot.send_message(chat_id, f"Гравець {games[chat_id]['players']['X']} чекає на другого гравця для приєднання.",
                     reply_markup=join_markup)


# Приєднання до гри
@bot.callback_query_handler(func=lambda call: call.data == "join_game")
def join_game(call):
    chat_id = call.message.chat.id
    game = games.get(chat_id)

    if not game:
        bot.send_message(chat_id, "Немає активної гри, до якої можна приєднатися.")
        return

    if game["mode"] != "player":
        bot.send_message(chat_id, "Це гра проти бота. Ви не можете приєднатися.")
        return

    if game["players"]["O"] is not None:
        bot.send_message(chat_id, "У цій грі вже є два гравці.")
        return

    if call.from_user.first_name == game["players"]["X"]:
        bot.send_message(chat_id, "Ви вже граєте в цій грі.")
        return

    # Приєднання другого гравця
    game["players"]["O"] = call.from_user.first_name

    # Оновлення повідомлення про гравців
    player_info = f"Гравці:\n{game['players']['X']} (X) vs {game['players']['O']} (O)"
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=player_info)

    # Повідомлення про початок гри з ніком другого гравця
    bot.send_message(chat_id, f"{game['players']['O']} приєднався! Починаємо гру.")

    # Хід гравця X
    bot.send_message(chat_id, f"X ({game['players']['X']}) робить перший хід.", reply_markup=generate_markup(chat_id))


# інлайн-клавіатура для гри
def generate_markup(chat_id):
    board = games[chat_id]["board"]
    markup = types.InlineKeyboardMarkup(row_width=3)

    for i in range(3):
        buttons = []
        for j in range(3):
            buttons.append(types.InlineKeyboardButton(board[i][j], callback_data=f"{i}{j}"))
        markup.add(*buttons)

    return markup


# взаємодія з інлайн-кнопками
@bot.callback_query_handler(func=lambda call: call.data and len(call.data) == 2)
def callback_game(call):
    chat_id = call.message.chat.id
    game = games.get(chat_id)
    if not game:
        return

    board = game["board"]
    current_player = game.get("turn")
    if not current_player:
        bot.answer_callback_query(call.id, "Гра не розпочата.")
        return

    player_name = game["players"].get(current_player)
    player_id = call.from_user.first_name

    if player_name != player_id:
        bot.answer_callback_query(call.id, "Це не ваш хід!")
        return

    row, col = int(call.data[0]), int(call.data[1])

    if board[row][col] == " ":
        board[row][col] = current_player
        if check_winner(board, current_player):
            bot.edit_message_text(f"Гравець {player_name} ({current_player}) виграв!\n{render_board(board)}", chat_id,
                                  call.message.message_id)
            games.pop(chat_id)
        elif is_board_full(board):
            bot.edit_message_text(f"Нічия!\n{render_board(board)}", chat_id, call.message.message_id)
            games.pop(chat_id)
        else:
            game["turn"] = "O" if current_player == "X" else "X"
            next_player_name = game["players"][game["turn"]]
            bot.edit_message_text(f"Хід гравця {next_player_name} ({game['turn']})", chat_id, call.message.message_id,
                                  reply_markup=generate_markup(chat_id))

            if game["mode"] == "bot" and game["turn"] == "O":
                bot_move(chat_id)


# Випадковий хід бота
def bot_move(chat_id):
    game = games[chat_id]
    board = game["board"]

    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    if not empty_cells:
        return  # Нет доступных ячеек, ничего не делаем

    row, col = random.choice(empty_cells)
    board[row][col] = "O"

    if check_winner(board, "O"):
        bot.send_message(chat_id, f"Бот виграв!\n{render_board(board)}")
        games.pop(chat_id)
    elif is_board_full(board):
        bot.send_message(chat_id, f"Нічия!\n{render_board(board)}")
        games.pop(chat_id)
    else:
        game["turn"] = "X"  # Сменить ход на игрока X
        next_player_name = game["players"]["X"]
        bot.send_message(chat_id, f"Хід гравця {next_player_name} ({game['turn']})",
                         reply_markup=generate_markup(chat_id))


# Запуск бота
bot.polling()