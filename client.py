import telebot
from os import environ, system, remove, path, makedirs, cpu_count
from uuid import uuid4
import threading

from voice_parser import recognise
from main import Bot
from ChatGPT_Request import ChangeModel, ChangeTimeout, GetGlobalVars


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


markup_inline = telebot.types.InlineKeyboardMarkup()
buttons = [
    telebot.types.InlineKeyboardButton(text='note', callback_data='note'),
    telebot.types.InlineKeyboardButton(text='notice', callback_data='notice'),
    telebot.types.InlineKeyboardButton(text='delete', callback_data='delete'),
    telebot.types.InlineKeyboardButton(text='get', callback_data='get'),
    telebot.types.InlineKeyboardButton(text='help', callback_data='help'),
]
markup_inline.add(*buttons)


@client.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print(f'call `{call.data}`, from user {call.from_user.id}-{call.from_user.username}')
    try:
        if call.data in Bot.commands_dict.keys():
            response = Bot.commands_dict[call.data](call.message)
            echo = client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=str(response),
                parse_mode="MarkdownV2",
                reply_markup=markup_inline
            )

            # if command had 'echo' function
            if response.echo is not None:
                client.register_next_step_handler(
                    message=echo,
                    callback=base_wrapper(response.echo)
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
        echo = client.send_message(
            chat_id=args[0].chat.id,
            text=str(response),
            parse_mode="MarkdownV2",
            reply_markup=markup_inline
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
            ready_notice = Bot.noticesPolling()
            client.send_message(
                chat_id=ready_notice[1],
                text=str(ready_notice[2]),
                parse_mode="MarkdownV2"
            )
        except:
            pass


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
            if opt == 'data':
                data = Bot.GetData()
                print(f'> {data}')
            if opt[:8] == 'setmodel':
                if ChangeModel(opt[9:]):
                    print(f'> Now using gpt model: {opt[9:]}')
                else:
                    print('> Invalid model name, availible models: "gpt-3.5t", "gpt-4"')
            if opt[:10] == 'settimeout':
                if ChangeTimeout(opt[11:]):
                    print(f'> Now gpt request timeout: {opt[11:]}')
                else:
                    print('> Invalid timeout value, availible timeout range: 5 - 300 sec')
            if opt == 'getvars':
                data = GetGlobalVars()
                print(f"> model: {data['model'].name}\n> timeout: {data['timeout']}")
        except:
            pass


def start_polling():
    """ bot start infinity polling """

    if environ.get("TOKEN") is None:
        print("Error: bot token is not defined")
        return

    wrap_commands()

    threads.extend([threading.Thread(target=notices_polling), threading.Thread(target=commandline_polling)])

    for thread in threads:
        thread.start()

    print("Start polling")
    client.polling()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_polling()

