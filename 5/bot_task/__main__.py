from db.db_api import init_db
from bot_runner.bot import bot

if __name__ == '__main__':
    init_db(force=True)
    bot.polling()
