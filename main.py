import telebot
from telebot import types
import json
import os

TOKEN = 'ВСТАВЬТЕ_СВОЙ_ТОКЕН'
bot = telebot.TeleBot(TOKEN)

DEFAULT_EXPENSE_CATEGORIES = [
    "🍔 Еда", "🏠 Жилье", "🚗 Транспорт", "👕 Одежда",
    "📱 Связь", "🎮 Развлечения", "💊 Здоровье", "📚 Образование"
]

DEFAULT_INCOME_CATEGORIES = [
    "💰 Зарплата", "💼 Подработка", "📈 Инвестиции", "🎁 Подарки",
    "💸 Кэшбэк", "🏦 Проценты", "🔄 Возврат долга", "🎰 Другое"
]

def get_user_file_path(user_id):
    return f"user_{user_id}_data.json"

def load_user_data(user_id):
    file_path = get_user_file_path(user_id)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        default_data = {
            'categories': {
                'expense': DEFAULT_EXPENSE_CATEGORIES.copy(),
                'income': DEFAULT_INCOME_CATEGORIES.copy()
            },
            'transactions': []
        }
        save_user_data(user_id, default_data)
        return default_data

def save_user_data(user_id, data):
    file_path = get_user_file_path(user_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    load_user_data(user_id)
    bot.send_message(
        message.chat.id,
        f"Здравствуйте, {user_name}! Я бот для учета финансов.\n\nВыберите действие:",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    bot.send_message(message.chat.id, f"Вы нажали: {message.text}")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()