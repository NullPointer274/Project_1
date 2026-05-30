import telebot
from telebot import types
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

TOKEN = 'ВСТАВЬТЕ_СВОЙ_ТОКЕН'
bot = telebot.TeleBot(TOKEN)

user_data = {}

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


def get_user_expense_categories(user_id):
    data = load_user_data(user_id)
    return data['categories']['expense']


def get_user_income_categories(user_id):
    data = load_user_data(user_id)
    return data['categories']['income']


def add_user_expense_category(user_id, category):
    data = load_user_data(user_id)
    if category not in data['categories']['expense']:
        data['categories']['expense'].append(category)
        save_user_data(user_id, data)
        return True
    return False


def add_user_income_category(user_id, category):
    data = load_user_data(user_id)
    if category not in data['categories']['income']:
        data['categories']['income'].append(category)
        save_user_data(user_id, data)
        return True
    return False


def add_transaction(user_id, transaction_type, category, amount):
    data = load_user_data(user_id)
    transaction = {
        'id': len(data['transactions']) + 1,
        'type': transaction_type,
        'category': category,
        'amount': amount,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'timestamp': datetime.now().timestamp()
    }
    data['transactions'].append(transaction)
    save_user_data(user_id, data)
    return transaction


def get_last_transactions(user_id, limit=5):
    data = load_user_data(user_id)
    transactions = data['transactions'][-limit:]
    return list(reversed(transactions))


def parse_date(date_str):
    formats = ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    date_str_lower = date_str.lower()
    if date_str_lower in ['сегодня', 'today']:
        return datetime.now()
    elif date_str_lower in ['вчера', 'yesterday']:
        return datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)
    return None


def get_transactions_in_period(user_id, start_date, end_date):
    data = load_user_data(user_id)
    transactions = data['transactions']
    start_ts = datetime(start_date.year, start_date.month, start_date.day).timestamp()
    end_ts = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59).timestamp()
    return [t for t in transactions if start_ts <= t['timestamp'] <= end_ts]


def get_statistics_for_period(transactions):
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expense

    expense_by_category = defaultdict(float)
    income_by_category = defaultdict(float)
    for t in transactions:
        if t['type'] == 'expense':
            expense_by_category[t['category']] += t['amount']
        else:
            income_by_category[t['category']] += t['amount']

    expense_by_category = dict(sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True))
    income_by_category = dict(sorted(income_by_category.items(), key=lambda x: x[1], reverse=True))

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'expense_by_category': expense_by_category,
        'income_by_category': income_by_category,
        'count': len(transactions)
    }


def format_statistics_message(stats, start_date, end_date):
    start_str = start_date.strftime("%d.%m.%Y")
    end_str = end_date.strftime("%d.%m.%Y")
    period_str = f"за {start_str}" if start_date == end_date else f"с {start_str} по {end_str}"

    message = f"📊 **Статистика {period_str}:**\n\n"
    message += f"💰 **Доходы:** {stats['total_income']:,.2f} руб.\n"
    message += f"💸 **Расходы:** {stats['total_expense']:,.2f} руб.\n"
    message += f"⚖️ **Баланс:** {stats['balance']:,.2f} руб.\n"
    message += f"📝 **Операций:** {stats['count']}\n"
    return message


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


def expense_categories_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    categories = get_user_expense_categories(user_id)
    buttons = [types.KeyboardButton(cat) for cat in categories]
    buttons.append(types.KeyboardButton("🔙 Назад"))
    keyboard.add(*buttons)
    return keyboard


def income_categories_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    categories = get_user_income_categories(user_id)
    buttons = [types.KeyboardButton(cat) for cat in categories]
    buttons.append(types.KeyboardButton("🔙 Назад"))
    keyboard.add(*buttons)
    return keyboard


def category_type_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("💰 Для расходов"),
        types.KeyboardButton("📈 Для доходов"),
        types.KeyboardButton("🔙 Назад")
    ]
    keyboard.add(*buttons)
    return keyboard


def statistics_options_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("📊 Текстовая статистика"),
        types.KeyboardButton("🔙 Назад")
    ]
    keyboard.add(*buttons)
    return keyboard


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("❌ Отмена"))
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
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    if text == "❌ Отмена":
        if chat_id in user_data:
            del user_data[chat_id]
        bot.send_message(chat_id, "Действие отменено.", reply_markup=main_keyboard())
        return

    if text == "🔙 Назад":
        if chat_id in user_data:
            del user_data[chat_id]
        bot.send_message(chat_id, "Выберите действие:", reply_markup=main_keyboard())
        return

    if text == "📊 Статистика":
        user_data[chat_id] = {'action': 'statistics_choice'}
        bot.send_message(chat_id, "📊 Выберите тип статистики:", reply_markup=statistics_options_keyboard())
        return

    if chat_id in user_data and user_data[chat_id].get('action') == 'statistics_choice':
        if text == "📊 Текстовая статистика":
            user_data[chat_id]['stat_type'] = text
            user_data[chat_id]['action'] = 'waiting_start_date'
            bot.send_message(chat_id, "📅 Введите начальную дату (ДД.ММ.ГГГГ, сегодня, вчера):",
                             reply_markup=cancel_keyboard())
        else:
            bot.send_message(chat_id, "Выберите тип:", reply_markup=statistics_options_keyboard())
        return

    if chat_id in user_data and user_data[chat_id].get('action') == 'waiting_start_date':
        start_date = parse_date(text)
        if start_date:
            user_data[chat_id]['start_date'] = start_date
            user_data[chat_id]['action'] = 'waiting_end_date'
            bot.send_message(chat_id, f"Начало: {start_date.strftime('%d.%m.%Y')}\nВведите конечную дату:",
                             reply_markup=cancel_keyboard())
        else:
            bot.send_message(chat_id, "❌ Неверный формат. Попробуйте снова:", reply_markup=cancel_keyboard())
        return

    if chat_id in user_data and user_data[chat_id].get('action') == 'waiting_end_date':
        end_date = parse_date(text)
        if end_date:
            start_date = user_data[chat_id]['start_date']
            if end_date < start_date:
                bot.send_message(chat_id, "❌ Конечная дата не может быть раньше начальной.",
                                 reply_markup=cancel_keyboard())
                return

            transactions = get_transactions_in_period(user_id, start_date, end_date)
            stats = get_statistics_for_period(transactions)
            response = format_statistics_message(stats, start_date, end_date)
            bot.send_message(chat_id, response, parse_mode='Markdown', reply_markup=main_keyboard())
            del user_data[chat_id]
        else:
            bot.send_message(chat_id, "❌ Неверный формат. Попробуйте снова:", reply_markup=cancel_keyboard())
        return

    if text == "📋 Мои категории":
        expense_cats = get_user_expense_categories(user_id)
        income_cats = get_user_income_categories(user_id)
        expense_list = "\n".join([f"  • {cat}" for cat in expense_cats])
        income_list = "\n".join([f"  • {cat}" for cat in income_cats])
        bot.send_message(chat_id,
                         f"📋 **Ваши категории:**\n\n💰 **Расходы:**\n{expense_list}\n\n📈 **Доходы:**\n{income_list}",
                         parse_mode='Markdown', reply_markup=main_keyboard())
        return

    if text == "📜 Последние операции":
        transactions = get_last_transactions(user_id, 5)
        if not transactions:
            bot.send_message(chat_id, "📭 Нет операций", reply_markup=main_keyboard())
            return
        response = "📜 **Последние 5 операций:**\n\n"
        for t in transactions:
            emoji = "🔴" if t['type'] == 'expense' else "🟢"
            type_text = "Расход" if t['type'] == 'expense' else "Доход"
            response += f"{emoji} *{type_text}*: {t['amount']:,.2f} руб.\n   📌 {t['category']}\n   🕐 {t['date']}\n\n"
        bot.send_message(chat_id, response, parse_mode='Markdown', reply_markup=main_keyboard())
        return

    if text == "➕ Добавить категорию":
        user_data[chat_id] = {'step': 'category_type'}
        bot.send_message(chat_id, "Для чего добавить категорию?", reply_markup=category_type_keyboard())
        return

    if chat_id in user_data and user_data[chat_id].get('step') == 'category_type':
        if text == "💰 Для расходов":
            user_data[chat_id]['category_type'] = 'expense'
            user_data[chat_id]['step'] = 'new_category'
            bot.send_message(chat_id, "Введите название категории расходов:", reply_markup=cancel_keyboard())
        elif text == "📈 Для доходов":
            user_data[chat_id]['category_type'] = 'income'
            user_data[chat_id]['step'] = 'new_category'
            bot.send_message(chat_id, "Введите название категории доходов:", reply_markup=cancel_keyboard())
        else:
            bot.send_message(chat_id, "Выберите тип:", reply_markup=category_type_keyboard())
        return

    if chat_id in user_data and user_data[chat_id].get('step') == 'new_category':
        new_category = text.strip()
        if new_category:
            cat_type = user_data[chat_id]['category_type']
            if cat_type == 'expense':
                if add_user_expense_category(user_id, new_category):
                    bot.send_message(chat_id, f"✅ Категория '{new_category}' добавлена!", reply_markup=main_keyboard())
                else:
                    bot.send_message(chat_id, "❌ Категория уже существует!", reply_markup=main_keyboard())
            else:
                if add_user_income_category(user_id, new_category):
                    bot.send_message(chat_id, f"✅ Категория '{new_category}' добавлена!", reply_markup=main_keyboard())
                else:
                    bot.send_message(chat_id, "❌ Категория уже существует!", reply_markup=main_keyboard())
            del user_data[chat_id]
        else:
            bot.send_message(chat_id, "❌ Введите название:", reply_markup=cancel_keyboard())
        return

    if text == "💰 Расход":
        user_data[chat_id] = {'action': 'expense'}
        bot.send_message(chat_id, "Выберите категорию:", reply_markup=expense_categories_keyboard(user_id))
        return

    if text == "📈 Доход":
        user_data[chat_id] = {'action': 'income'}
        bot.send_message(chat_id, "Выберите категорию:", reply_markup=income_categories_keyboard(user_id))
        return

    if chat_id in user_data and user_data[chat_id].get('action') in ['expense', 'income'] and 'category' not in \
            user_data[chat_id]:
        cats = get_user_expense_categories(user_id) if user_data[chat_id][
                                                           'action'] == 'expense' else get_user_income_categories(
            user_id)
        if text in cats:
            user_data[chat_id]['category'] = text
            bot.send_message(chat_id, "Введите сумму:", reply_markup=cancel_keyboard())
        else:
            kb = expense_categories_keyboard(user_id) if user_data[chat_id][
                                                             'action'] == 'expense' else income_categories_keyboard(
                user_id)
            bot.send_message(chat_id, "Выберите из списка:", reply_markup=kb)
        return

    if chat_id in user_data and 'category' in user_data[chat_id]:
        try:
            amount = float(text.replace(',', '.'))
            if amount <= 0:
                raise ValueError
            action = user_data[chat_id]['action']
            category = user_data[chat_id]['category']
            add_transaction(user_id, action, category, amount)
            emoji = "🔴" if action == 'expense' else "🟢"
            type_text = "Расход" if action == 'expense' else "Доход"
            bot.send_message(chat_id, f"{emoji} **{type_text}** {amount:,.2f} руб. записан!", parse_mode='Markdown',
                             reply_markup=main_keyboard())
            del user_data[chat_id]
        except ValueError:
            bot.send_message(chat_id, "❌ Введите число:", reply_markup=cancel_keyboard())
        return

    bot.send_message(chat_id, f"Я не понимаю '{text}'.", reply_markup=main_keyboard())


if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()