import telebot
from os import environ

from main import Bot


token = environ.get("TOKEN")
client = telebot.TeleBot(token=token, 
                    parse_mode=None,
                    threaded=True,
                    num_threads=4
                    )


def command_wrapper(commands):
    ''' wrapper for bot commands '''
    def wrapper(func):
        @client.message_handler(commands=commands)
        def _wrapper(*args, **kwargs):
            responce = func(args[0])

            echo = client.send_message(
                chat_id=args[0].chat.id,
                text=responce
            )
            
            # if command had echo function
            if len(responce) == 2:
                client.register_next_step_handler(message=echo, callback=echo_command_wrapper(responce[1]))

        return _wrapper
    return wrapper


def echo_command_wrapper(func):
    ''' wrapper for echo commands '''
    def _wrapper(*args, **kwargs):
        responce = func(args[0])

        echo = client.send_message(
            chat_id=args[0].chat.id,
            text=responce
        )
        
        # if command had echo function
        if len(responce) == 2:
            client.register_next_step_handler(
                message=echo[0], 
                callback=wrap_commands(responce[1])
                )

    return _wrapper


def wrap_commands():
    ''' wraps all bot commands to telebot handlers '''
    for command in Bot.commands:
        command_wrapper(command[1])(command[0])


def start_polling():
    ''' bot start infinity polling '''
    print("start polling")
    client.infinity_polling()


if __name__ == "__main__":
    wrap_commands()
    start_polling()

