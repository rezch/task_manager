import telebot
from os import environ, system, remove, path, makedirs, cpu_count
from uuid import uuid4
import threading
from time import sleep

from voice_parser import recognise
from main import Bot
from gpt_request import ChangeModel, ChangeTimeout, ChangeAttempts, GetGlobalVars


token = environ.get("TOKEN")
client = telebot.TeleBot(token=token,
                         parse_mode=None,
                         threaded=True,
                         num_threads=cpu_count()
                         )


def getTextFromVoice(message):
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

    # deleting temp audio file
    remove(file_name_full)
    remove(file_name_full_converted)

    return text


@client.message_handler(content_types=['voice'])
def voiceMessageCommand(message, get=False):
    """ getting voice message from user """
    client.reply_to(message, getTextFromVoice(message))


buttons = [
    telebot.types.InlineKeyboardButton(text='note', callback_data='note'),
    telebot.types.InlineKeyboardButton(text='notice', callback_data='notice'),
    telebot.types.InlineKeyboardButton(text='delete', callback_data='delete'),
    telebot.types.InlineKeyboardButton(text='get', callback_data='get'),
    telebot.types.InlineKeyboardButton(text='help', callback_data='help'),
]
# buttons_yes_no = [
#     telebot.types.InlineKeyboardButton(text='Да', callback_data='yes'),
#     telebot.types.InlineKeyboardButton(text='Нет', callback_data='no'),
# ]


@client.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print(f'call `{call.data}`, from user {call.from_user.id}-{call.from_user.username}')
    try:
        if call.data in Bot.commands_dict.keys():
            response = Bot.commands_dict[call.data](call.message)
            keyboard = telebot.types.InlineKeyboardMarkup().add(*buttons) if response.keyboard is True else None
            echo = client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=str(response),
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )

            # if command had 'echo' function
            if response.echo is not None:
                client.register_next_step_handler(
                    message=echo,
                    callback=base_wrapper(response.echo),
                    parse_mode="MarkdownV2",
                )
    except telebot.apihelper.ApiTelegramException:
        pass


def base_wrapper(func):
    """ base inner wrapper for commands """
    def _wrapper(*args, **kwargs):
        if args[0].voice is not None: # if message type is voice
            args[0].text = getTextFromVoice(args[0])

        print(f'get command: `{args[0].text}`, from user {args[0].from_user.id}-{args[0].from_user.username}')
        response = func(args[0])  # -> ( response message, echo_func(opt) )

        if response.reply is not None:
            keyboard = telebot.types.InlineKeyboardMarkup().add(*buttons) if response.keyboard is True else None
            echo = client.reply_to(
                message=response.reply,
                text=str(response),
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
        else:
            keyboard = telebot.types.InlineKeyboardMarkup().add(*buttons) if response.keyboard is True else None
            echo = client.send_message(
                chat_id=args[0].chat.id,
                text=str(response),
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )

        # if command had 'echo' function
        if response.echo is not None:
            client.register_next_step_handler(
                message=echo,
                callback=base_wrapper(response.echo)
            )

    return _wrapper


def wrap_commands():
    """ wraps all bot commands to telebot handlers """

    for command in Bot.commands:
        client.message_handler(commands=command[1])(base_wrapper(command[0]))


threads = []
alive = True


def notices_polling():
    global alive
    while alive:
        try:
            sleep(1)
            ready_notice = Bot.noticesPolling()
            if ready_notice is None:
                continue
            print("Send notice:", ready_notice)
            client.send_message(
                chat_id=ready_notice[1],
                text=str(ready_notice[2])
            )
        except Exception as e:
            print(e, f'Cannot send notice: {ready_notice}')
            Bot.revertNotice(ready_notice)


def commandline_polling():
    global alive
    while True:
        try:
            opt = input()
            if opt == 'quit':
                print('> Stopping the bot')
                client.stop_polling()
                Bot.db.Dump()
                alive = False
                return
            elif opt == 'data':
                data = Bot.GetData()
                print(f'> {data}')
            elif opt[:8] == 'setmodel':
                if ChangeModel(opt[9:]):
                    print(f'> Now using gpt model: {opt[9:]}')
                else:
                    print('> Invalid model name, available models: "gpt-3.5t", "gpt-4"')
            elif opt[:10] == 'settimeout':
                if ChangeTimeout(opt[11:]):
                    print(f'> Now gpt request timeout: {opt[11:]}')
                else:
                    print('> Invalid timeout value, available timeout range: 5 - 300 sec')
            elif opt[:11] == 'setattempts':
                if ChangeAttempts(opt[12:]):
                    print(f'> Now gpt request attempts count: {opt[12:]}')
                else:
                    print(f'Invalid attempts count, available num: 1 - 10')
            elif opt == 'getvars':
                data = GetGlobalVars()
                print("".join([f'> {key}: {value}\n' for key, value in data.items()]))
        except Exception as e:
            print(e)


def start_polling():
    """ bot start infinity polling """
    global alive, threads

    if environ.get("TOKEN") is None:
        print("> Error: bot token is not defined")
        return

    wrap_commands()
    alive = True
    threads = []

    threads.extend([threading.Thread(target=notices_polling), threading.Thread(target=commandline_polling)])

    for thread in threads:
        thread.start()

    print("> Start polling")
    client.infinity_polling()

    print("> Joining the threads")
    for thread in threads:
        thread.join()
    print("> terminated")


if __name__ == "__main__":
    restart = True
    while restart:
        restart = False
        start_polling()

