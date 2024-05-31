from datetime import datetime
from time import sleep

from gpt_request import Request, RawGptRequest
from db import DB

HELP_MESSAGE = '''Привет, я бот помощник, с моей помощью ты сможешь хранить свои заметки, и попросить меня напомнить тебе о чем-то.

Основные команды:
/start - начать работу
/gpt - обратиться к сервису gpt4
/note или /add - добавить заметку
/notice или /reminder - добавить напоминание
/get - получить список своих заметок
/del или /delete - удалить заметку или напоминание
/help - получить информацию о командах

Боту можно отвечать голосовыми сообщениями, или писать текстом.
Для работы с уведомлениями, лучше помимо напоминания, уточнять день и время в которые вы хотите получить уведомление.'''


class UserResponse:
    def __init__(self):
        self.__data = {}

    def Get(self, user_id: str, command: str):
        try:
            return self.__data[user_id][command]
        except KeyError:
            return None

    def Set(self, user_id, command: str, data):
        if user_id not in self.__data.keys():
            self.__data[user_id] = {}

        self.__data[user_id][command] = data
        print(f'dump to {user_id}-{command}: {data}')


class Response:
    def __init__(self, message, echo=None, reply=None, keyboard: bool = True):
        self.message = Response.prepare_message(str(message))
        self.echo = echo
        self.reply = reply
        self.keyboard = keyboard

    @staticmethod
    def prepare_message(message: str) -> str:
        # telebot reserved charachters for markdown mode
        reserved = '_*~>#+-=|{}.!()'
        for char in reserved:
            message = message.replace(char, f'\{char}')
        if '[]' in message:
            message = message.replace('[]', '\[\]')
        print(f'response: {message}')
        return message

    def __iter__(self):
        yield from [self.message, self.echo]

    def __str__(self):
        return str(self.message)


class Mtx:
    def __init__(self):
        self.__lock = False

    def lock(self):
        while self.__lock == True:
            sleep(0)  # thread yield
        self.__lock = True

    def unlock(self):
        self.__lock = False


class Bot:
    """ bot commands
        args: message
        return: Response(message, next_step(opt))
    """

    __instance = None
    commands = []
    commands_dict = {}
    forward = UserResponse()
    db = DB("data.json")
    notices = None  # format: (datetime, char.id, data, notice)
    mtx = Mtx()

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls

    @staticmethod
    def GetData() -> dict:
        Bot.mtx.lock()
        data = Bot.db.getAllData()
        Bot.mtx.unlock()
        return data

    @staticmethod
    def LoadNotices() -> list:
        Bot.db.Dump()
        data = Bot.db.getAllData()
        result = []
        for user in data.keys():
            if 'notices' not in data[user].keys():
                continue
            for notice in data[user]['notices']:
                dt = datetime.strptime(notice['date'] + ' ' + notice['time'], '%d.%m.%Y %H:%M')
                result.append((dt, user, notice['info'], notice))
        return result

    @staticmethod
    def RemoveNoticeFromDB(notice) -> None:
        user_id = notice[1]
        notice_data = notice[3]
        data = Bot.db.getAllData()
        if 'notices' not in data[user_id].keys():
            return
        data[user_id]['notices'].remove(notice_data)

    @staticmethod
    def noticesPolling():
        Bot.mtx.lock()
        Bot.notices = Bot.LoadNotices()

        for notice in Bot.notices:
            now = datetime.now()
            if notice[0] < now:
                Bot.notices.remove(notice)
                Bot.RemoveNoticeFromDB(notice)
                Bot.db.Dump()
                Bot.mtx.unlock()
                return notice

        Bot.mtx.unlock()
        return None

    @staticmethod
    def revertNotice(notice: tuple) -> None:
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(notice[1])
        if 'notices' not in user_data.keys():
            user_data['notices'] = []
        user_data['notices'].append(notice[3])
        Bot.notices.append(notice[3])
        Bot.db.Dump()
        Bot.mtx.unlock()

    @staticmethod
    def startCommand(message):
        """ start command """
        global HELP_MESSAGE
        return Response(HELP_MESSAGE)

    @staticmethod
    def helloCommand(message):
        """ hello command """
        result = 'Hello '
        if message.from_user.first_name is None and message.from_user.last_name is None:
            return result + message.from_user.username
        if message.from_user.first_name is not None:
            result += message.from_user.first_name
        if message.from_user.last_name is not None:
            if len(result) > 6:
                result += ' '
            result += message.from_user.last_name
        return Response(result, reply=message)

    @staticmethod
    def gptEchoCommand(message):
        return Response(RawGptRequest(message.text), reply=message)

    @staticmethod
    def gptCommand(message):
        """ request to gpt """
        return Response("Какой у вас вопрос?", Bot.gptEchoCommand, keyboard=False)

    @staticmethod
    def addNoteCommand(message):
        """ add note start command """
        return Response("Что вы хотите записать?", Bot.addNoteEcho, keyboard=False)

    @staticmethod
    def addNoteEcho(message):
        """ adding note """
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id)
        if 'notes' not in user_data.keys():
            user_data['notes'] = []
        user_data['notes'].append(message.text)
        Bot.db.Dump()
        Bot.mtx.unlock()
        return Response("Заметка успешно добавлена", reply=message)

    @staticmethod
    def __prettyNotes(message) -> str:
        """ convert user notes list to formatted string for response """
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id).copy()
        Bot.mtx.unlock()

        response = ''
        if 'notes' in user_data.keys():
            response += ''.join([f'```{i + 1}: {note}```\n' for i, note in enumerate(user_data['notes'])])

        notes_count = 0 if 'notes' not in user_data.keys() else len(user_data['notes'])
        if 'notices' in user_data.keys():
            response += ''.join(
                [f'```{i + notes_count + 1}[напоминание]: {Bot.__prettyNotice(notice)}```\n' for i, notice in
                 enumerate(user_data['notices'])])
        if response == '':
            return "У вас пока нет никаких заметок"
        print(response)
        return response

    @staticmethod
    def getNoteCommand(message):
        """ returns user notes """
        return Response(Bot.__prettyNotes(message))

    @staticmethod
    def deleteNoteCommand(message):
        """ delete note start command """
        notes = Bot.__prettyNotes(message)
        if notes == "У вас пока нет никаких заметок":
            return Response(notes)
        return Response(f'{notes}\n Какую заметку вы хотите удалить?', Bot.deleteNoteEcho, keyboard=False)

    @staticmethod
    def deleteNoteEcho(message):
        """ deletes note """
        note_id = message.text
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id)

        if 'notes' not in user_data:
            user_data['notes'] = []
        if 'notices' not in user_data:
            user_data['notices'] = []

        notes_count = len(user_data['notes'])
        notices_count = len(user_data['notices'])

        try:
            note_id = int(note_id)
            if note_id > notes_count + notices_count or note_id < 1:
                Bot.mtx.unlock()
                raise ValueError
        except (ValueError, TypeError):
            Bot.mtx.unlock()
            return Response('Номер заметки указан не верно', reply=message)

        if note_id <= notes_count:
            user_data['notes'].pop(note_id - 1)
        else:
            user_data['notices'].pop(note_id - notes_count - 1)

        Bot.db.Dump()
        Bot.mtx.unlock()
        return Response('Заметка успешно удалена', reply=message)

    @staticmethod
    def addReminderCommand(message):
        return Response("О чем, и когда мне вам напомнить?", Bot.addReminderEcho, keyboard=False)

    @staticmethod
    def __prettyNotice(notice: dict) -> str:
        return f"`{notice['info']}` {notice['date']} в {notice['time']}"

    @staticmethod
    def addReminderEcho(message):
        gpt_response = Request(message.text)
        if gpt_response is None:
            return Response("Извините, не могу вас правильно понять", reply=message)
        if 'bad_value' in gpt_response.keys():
            return Response(gpt_response['bad_value'])
        Bot.forward.Set(message.chat.id, Bot.addReminderEcho.__name__, gpt_response)
        notice = Bot.__prettyNotice(gpt_response)
        return Response(f"Добавить это напоминание?\n{notice}", Bot.addReminderAccept, reply=message, keyboard=False)

    @staticmethod
    def addReminderAccept(message):
        response = str(message.text).lower()
        if response not in ['да', 'yes']:
            return Response('Напоминание не было добавлено')
        notice = Bot.forward.Get(message.chat.id, Bot.addReminderEcho.__name__)
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id)
        if 'notices' not in user_data.keys():
            user_data['notices'] = []
        user_data['notices'].append(notice)
        dt = datetime.strptime(notice['date'] + ' ' + notice['time'], '%d.%m.%Y %H:%M')
        Bot.notices.append((dt, message.chat.id, notice['info'], notice))
        Bot.db.Dump()
        Bot.mtx.unlock()
        return Response('Напоминание успешно добавлено')

    @staticmethod
    def helpCommand(message):
        global HELP_MESSAGE
        response = ''.join([line + '\n' for line in HELP_MESSAGE.split('\n')[1:]])
        return Response(response)

    @staticmethod
    def addFewNotes(message):
        return Response("Какие заметки вы хотите добавить?", Bot.addFewNotesEcho, keyboard=False)

    @staticmethod
    def addFewNotesEcho(message):
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id)
        if 'notes' not in user_data.keys():
            user_data['notes'] = []

        notes = message.text.split('\n')
        user_data['notes'].extend(notes)

        Bot.db.Dump()
        Bot.mtx.unlock()
        return Response("Заметка успешно добавлена", reply=message)


''' list of bot commands 
    ( command function, list of command start key word )
    * only for single commands or root commands that starts echo *
'''
Bot.commands = [
    (Bot.startCommand, ['start']),
    (Bot.helloCommand, ['hello']),
    (Bot.gptCommand, ['gpt']),
    (Bot.addNoteCommand, ['note', 'add']),
    (Bot.getNoteCommand, ['get']),
    (Bot.deleteNoteCommand, ['del', 'delete']),
    (Bot.addReminderCommand, ['reminder', 'notice']),
    (Bot.helpCommand, ['help']),
    (Bot.addFewNotes, ['notes']),
]

Bot.commands_dict = {
    'start': Bot.startCommand,
    'hello': Bot.helloCommand,
    'gpt': Bot.gptCommand,
    'note': Bot.addNoteCommand,
    'get': Bot.getNoteCommand,
    'delete': Bot.deleteNoteCommand,
    'notice': Bot.addReminderCommand,
    'help': Bot.helpCommand,
    'notes': Bot.addFewNotes,
}


if __name__ == "__main__":
    pass
