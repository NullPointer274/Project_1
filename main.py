import telebot

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет!")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()