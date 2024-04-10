import telebot
from os import environ

from main import Bot


bot = Bot()
token = environ.get("TOKEN")
client = telebot.TeleBot(token=token, 
                    parse_mode=None,
                    threaded=True,
                    num_threads=4
                    )



@client.message_handler(commands='<command_name>')
def some_command(message):
    responce = bot.someCommand(message)

    client.send_message(
        chat_id=message.chat.id,
        text=responce
    )


if __name__ == "__main__":
    bot.infinity_polling()
    
