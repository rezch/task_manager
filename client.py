import telebot
from os import environ, system, remove, path, makedirs
from uuid import uuid4
from voice_parser import recognise

from main import Bot

token = environ.get("TOKEN")
client = telebot.TeleBot(token=token,
                         parse_mode=None,
                         threaded=True,
                         num_threads=4
                         )


@client.message_handler(content_types=['voice'])
def voiceMessageCommand(message):
    """ getting voice message from user """

    # getting data from voice message file
    voice_file_path = "./voice/"
    ready_voice_file_path = "./ready/"

    filename = str(uuid4())

    file_name_full = voice_file_path + filename + ".ogg"
    file_name_full_converted = ready_voice_file_path + filename + ".wav"

    if not path.exists(voice_file_path):
        makedirs(voice_file_path)

    if not path.exists(ready_voice_file_path):
        makedirs(ready_voice_file_path)

    # downloading voice message
    file_info = client.get_file(message.voice.file_id)
    downloaded_file = client.download_file(file_info.file_path)

    with open(file_name_full, 'ba') as new_file:
        new_file.write(downloaded_file)

    system("ffmpeg -i " + file_name_full + "  " + file_name_full_converted)

    # parsing text from voice message
    text = recognise(file_name_full_converted)
    client.reply_to(message, text)

    # deleting temp audio file
    remove(file_name_full)
    remove(file_name_full_converted)


def base_wrapper(func):
    """ base inner wrapper for commands """

    def _wrapper(*args, **kwargs):
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
                callback=base_wrapper(response[1])
            )

    return _wrapper


def command_wrapper(commands):
    """ wrapper for bot commands """

    def wrapper(func):
        return client.message_handler(commands=commands)(base_wrapper(func))

    return wrapper


def wrap_commands():
    """ wraps all bot commands to telebot handlers """

    for command in Bot.commands:
        command_wrapper(command[1])(command[0])


def start_polling():
    """ bot start infinity polling """

    if environ.get("TOKEN") is None:
        print("Error: bot token is not defined")
        return

    wrap_commands()
    print("Start polling")
    client.infinity_polling()


if __name__ == "__main__":
    start_polling()

