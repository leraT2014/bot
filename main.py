import  telebot
from random import randint
from datetime import datetime
import requests
import os
import gdown
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode=None)

app =Flask(__name__)

@app.route('/')
def index():
    return "Бот запущен"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_update([update])
    return '', 200


@bot.message_handler(commands=["start"])
def send_welcome(message):
    try:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = telebot.types.KeyboardButton(text="Игра в кубик")
        button2 = telebot.types.KeyboardButton(text="Игровой автомат")
        button3 = telebot.types.KeyboardButton(text="Отгадай число")
        keyboard.add(button1, button2)
        bot.send_message(message.chat.id,"Привет я бот", reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")



@bot.message_handler(commands=["date"])
def date(message):
    try:
        bot.send_message(message.chat.id, "Сейчас: " + str(datetime.today()))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


@bot.message_handler(commands=["random"])
def random(message):
    try:
        bot.send_message(message.chat.id, "Случайное число: " + str(randint(1, 50)))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(commands=['image'])
def send_image(message):
    try:
        file = open("image.jpg", 'rb')
        bot.send_photo(message.chat.id, file, caption="Изображение собаки: ")
        file.close()
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

 

@bot.message_handler(content_types=["text"])
def answer(message):
    try:
        text = message.text
        if text == "Привет":
            bot.send_message(message.chat.id, "Привет")
        elif text == "Как дела":
            bot.send_message(message.chat.id, "отлично,как у тебя")
        elif text == "Норм":
            bot.send_message(message.chat.id,"Класс")
        elif text == "Как тебя зовут":
            bot.send_message(message.chat.id, "Ботяро")
        elif text == "Сколько тебе лет":
            bot.send_message(message.chat.id, "Я виртуалиный у меня нет возраста")
        elif text == "Раскажи шутку":
            bot.send_message(message.chat.id, "малыш в зоопарке говорит маме: -Мама, смотри обезьянка в очках! -тихо это кассир.")
        elif text == "Хочу еще шутку":
            bot.send_message(message.chat.id, "-ты где? -в аду - как из школы выйдешь позвони")
        elif text == "Хочешь прикол":
            bot.send_message(message.chat.id, "нет давай я")
        elif text == "Нет я":
            bot.send_message(message.chat.id, "нет давай я")
        elif text == "Нет":
            bot.send_message(message.chat.id, "да")
        elif text == "Ладно ты":
            bot.send_message(message.chat.id, "без паники ты не старенький")
        elif text == "ХАХА круто":
            bot.send_message(message.chat.id, "ага")


        elif text == "Отгадай число":

            keyboard3 = telebot.types.InlineKeyboardMarkup(row_width=3)
            butoton1 = telebot.types.InlineKeyboardButton("1", callback_data="1")
            butoton2 = telebot.types.InlineKeyboardButton("2", callback_data="2")
            butoton3 = telebot.types.InlineKeyboardButton("3", callback_data="3")
            butoton4 = telebot.types.InlineKeyboardButton("4", callback_data="4")
            butoton5 = telebot.types.InlineKeyboardButton("5", callback_data="5")
            butoton6 = telebot.types.InlineKeyboardButton("6", callback_data="6")
            keyboard3.add(butoton1, butoton2, butoton3, butoton4, butoton5, butoton6)
            bot.send_message(message.chat.id, "Угадай число которое я загадал", reply_markup=keyboard3)
        elif text == "Игровой автомат":
            value = bot.send_dice(message.chat.id, emoji='🎰').dice.value
            if value in (1, 16, 22, 32, 43, 48):
                bot.send_message(message.chat.id, "Победа")
            elif value == 64:
                bot.send_message(message.chat.id, "Jackpot!")
            else:
                bot.send_message(message.chat.id, "Попробуй еще раз")
        elif text == "Игра в кубик":

            keyboard2 = telebot.types.InlineKeyboardMarkup(row_width=3)
            butoton1 = telebot.types.InlineKeyboardButton("1", callback_data="1")
            butoton2 = telebot.types.InlineKeyboardButton("2", callback_data="2")
            butoton3 = telebot.types.InlineKeyboardButton("3", callback_data="3")
            butoton4 = telebot.types.InlineKeyboardButton("4", callback_data="4")
            butoton5 = telebot.types.InlineKeyboardButton("5", callback_data="5")
            butoton6 = telebot.types.InlineKeyboardButton("6", callback_data="6")
            keyboard2.add(butoton1, butoton2, butoton3, butoton4, butoton5, butoton6)
            bot.send_message(message.chat.id, "Угадай число на кубике", reply_markup=keyboard2)
        else:
            bot.send_message(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.callback_query_handler(func=lambda call: call.data in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
def dice_answer(call):
    value = bot.send_dice(call.message.chat.id,  emoji='')
    if str(value) == call.data:
        bot.send_message(call.message.chat.id, "Победа")
    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")


@bot.callback_query_handler(func=lambda call:call.data in ('1', '2', '3', '4', '5', '6'))
def dice_answer(call):
    value = bot.send_dice(call.message.chat.id, emoji='').dice_value
    if str(value) == call.data:
        bot.send_message(call.message.chat.id, "Победа")
    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")



if __name__ == "__main__":
    server_url = os.getenv("RENDER_EXTERNAL_URL")
    if server_url and TOKEN:
        webhook_url = f"{server_url}/{TOKEN}"
        set_webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(set_webhook_url)
            print("Webhook установлен:", r.text)
        except Exception as e:
            print("Ошибка при установке webhook:", e)

        port = int(os.environ.get("PORT", 10000))
        print(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port)
    else:
        print("Запуск бота в режиме pooling")
        bot.remove_webhook()
        bot.polling(none_stop=True)
