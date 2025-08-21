import json
import telebot
from random import randint
from datetime import datetime
import time
import random
import telebot
import requests
import os
import gdown
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
from flask import Flask, request
import re

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
    bot.process_new_updates([update])
    return '', 200

def escape_markdown(text: str) -> str:
    escape_chars = r'[_*[\]()~`>#+\-=|{}.!]'
    return re.sub(f'({escape_chars})', r'\\\1', text)

MAX_LEN = 4096

def send_long_message(chat_id, text, parse_mode="MarkdownV2"):
    safe_text = escape_markdown(text)
    for i in range(0, len(safe_text), MAX_LEN):
        bot.send_message(chat_id, safe_text[i:i+MAX_LEN], parse_mode=parse_mode)
    

def load_photo(message, name):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = name
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)

history_file = "history.json"
history = {}

if os.path.exists(history_file):
    try:
        with open(history_file, "r", encoding='utf-8') as f:
            history = json.load(f)
    except Exception:
        history = {}

def save_history():
    try:
        with open(history_file, "w", encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Ошибка сохранения истории: ", e)
        
def chat(user_id, text):
    try:
        if str(user_id) not in history:
            history[str(user_id)] = [
                {"role": "system", "content": "Ты — дружелюбный помощник."}
            ]

        history[str(user_id)].append({"role": "user", "content": text})

        if len(history[str(user_id)]) > 16:
            history[str(user_id)] = [history[str(user_id)][0]] + history[str(user_id)][-15:]

        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('API_KEY')}"
        }
        data = {
            "model": "deepseek-ai/DeepSeek-R1-0528",
            "messages": history[str(user_id)]
        }

        response = requests.post(url, headers=headers, json=data)
        data = response.json()

        if 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
            history[str(user_id)].append({"role": "assistant", "content": content})

            if len(history[str(user_id)]) > 16:
                history[str(user_id)] = [history[str(user_id)][0]] + history[str(user_id)][-15:]

            save_history()

            if '</think>' in content:
                return content.split('</think>', 1)[1]
            return content
        else:
            return f"Ошибка API: {data}"
    except Exception as e:
        return f"Ошибка при запросе: {e}"
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
        if text == "Отгадай число":
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
            bot.send_message(message.chat.id, "Думаю над ответом...")
            answer = chat(message.chat.id, message.text)
            send_long_message(message.chat.id, answer, parse_mode="MarkdownV2")
            bot.delete_message(message.chat.id, message.id+1)
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
