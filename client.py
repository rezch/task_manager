import telebot
from os import environ

from main import Bot

token = environ.get("TOKEN")
client = telebot.TeleBot(token=token,
                         parse_mode=None,
                         threaded=True,
                         num_threads=4
                         )


def base_wrapper(func):
    def _wrapper(*args, **kwargs):
        """ base inner wrapper for commands """
        response = func(args[0])  # -> ( response message, echo_func(opt) )

        if not isinstance(response, tuple):
            response = (response, None)

        echo = client.send_message(
            chat_id=args[0].chat.id,
            text=str(response[0])
        )

        # if command had 'echo' function
        if response[1] is not None:
            client.register_next_step_handler(
                message=echo,
                callback=echo_command_wrapper(response[1])
            )

    return _wrapper


def command_wrapper(commands):
    """ wrapper for bot commands """

    def wrapper(func):
        return client.message_handler(commands=commands)(base_wrapper(func))

    return wrapper


def echo_command_wrapper(func):
    """ wrapper for echo commands """
    return base_wrapper(func)


def wrap_commands():
    """ wraps all bot commands to telebot handlers """
    for command in Bot.commands:
        command_wrapper(command[1])(command[0])


def start_polling():
    """ bot start infinity polling """
    print("start polling")
    client.infinity_polling()


if __name__ == "__main__":
    wrap_commands()
    start_polling()
