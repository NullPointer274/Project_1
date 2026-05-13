import telebot
from telebot import types

TOKEN = 'ВСТАВЬТЕ_СВОЙ_ТОКЕН'
bot = telebot.TeleBot(TOKEN)

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("💰 Расход"),
        types.KeyboardButton("📈 Доход"),
        types.KeyboardButton("📊 Статистика"),
        types.KeyboardButton("➕ Добавить категорию"),
        types.KeyboardButton("📋 Мои категории"),
        types.KeyboardButton("📜 Последние операции")
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для учета финансов.\n\nВыберите действие:",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    bot.send_message(message.chat.id, f"Вы нажали: {message.text}")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()