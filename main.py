from datetime import datetime
from time import sleep

from ChatGPT_Request import RequestEvent, ParseRequest, ParseException
from db import DB


class UserResponse:
    def __init__(self):
        self.__data = {}

    def Get(self, user_id: str, command: str):
        try:
            return self.__data[user_id][command]
        except KeyError:
            return None

    def Set(self, user_id: str, command: str, data):
        if user_id not in self.__data.keys():
            self.__data[user_id] = {}

        self.__data[user_id][command] = data
        print(f'dump to {user_id}-{command}: {data}')


class Response:
    def __init__(self, message, echo=None):
        self.message = message.replace('.', '\.')
        self.echo = echo

    def __iter__(self):
        yield from [self.message, self.echo]

    def __str__(self):
        return str(self.message)


class Mtx:
    def __init__(self):
        self.__lock = False

    def lock(self):
        while self.__lock == True:
            sleep(0.1)
        self.__lock = True

    def unlock(self):
        self.__lock = False


class Bot:
    """ bot commands
        args: message
        return: Response(message, next_step(opt))
    """

    __instance = None
    forward = UserResponse()
    db = DB("data.json")
    notices = None  # format: (datetime, user_id, data, notice)
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
    def noticesPolling() -> list:
        Bot.mtx.lock()
        Bot.notices = Bot.LoadNotices()

        ready_notices = None
        for notice in Bot.notices:
            now = datetime.now()
            if notice[0] < now:
                ready_notices = (notice[0], notice[1], notice[2])
                Bot.notices.remove(notice)
                Bot.RemoveNoticeFromDB(notice)
                break
        
        Bot.db.Dump()
        Bot.mtx.unlock()
        sleep(1)
        if ready_notices is None:
            return None
        return (ready_notices[1], ready_notices[2])

    @staticmethod
    def startCommand(message):
        """ start command """
        return Response('Start')

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
        return Response(result)

    @staticmethod
    def gptEchoCommand(message):
        try:
            response = RequestEvent(message.text)
        except:
            response = 'Извините, сервис gpt4 временно не доступен'
        return Response(response)

    @staticmethod
    def gptCommand(message):
        """ request to gpt """
        return Response("Какой у вас вопрос?", Bot.gptEchoCommand)

    @staticmethod
    def addNoteCommand(message):
        """ add note start command """
        return Response("Что вы хотите записать?", Bot.addNoteEcho)

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
        return Response("Заметка успешно добавлена")

    @staticmethod
    def __prettyNotes(message) -> str:
        """ convert user notes list to formatted string for response """
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id)

        data = []
        if 'notes' in user_data.keys():
            data.extend(user_data['notes'])

        notes_ind = len(data)
        if 'notices' in user_data.keys() and user_data['notices'] != []:
            notices = []
            for notice in user_data['notices']:
                notices.append(Bot.__prettyNotice(notice))

            data.extend(notices)
        Bot.mtx.unlock()
        if not data:
            return "У вас пока нет никаких заметок"

        result = ''
        for i, note in enumerate(data):
            if i < notes_ind:
                result += f'```{i + 1}: {note}\n```'
            else:
                result += f'```{i + 1}-напоминание: {note}\n```'
        return result

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
        return Response(f'{notes}\n Какую заметку вы хотите удалить?', Bot.deleteNoteEcho)

    @staticmethod
    def deleteNoteEcho(message):
        """ deletes note """
        note_id = message.text
        Bot.mtx.lock()
        user_data = Bot.db.getUserData(message.chat.id)
        try:
            note_id = int(note_id)
            if note_id > len(user_data['notes']) or note_id < 1:
                Bot.mtx.unlock()
                raise TypeError
        except TypeError:
            Bot.mtx.unlock()
            return Response('Номер заметки указан не верно')
        user_data['notes'].pop(note_id - 1)
        Bot.db.Dump()
        Bot.mtx.unlock()
        return Response('Заметка успешно удалена')

    @staticmethod
    def addReminderCommand(message):
        return Response("О чем, и когда мне вам напомнить?", Bot.addReminderEcho)

    @staticmethod
    def __prettyNotice(notise: dict) -> str:
        return f"`{notise['info']}` {notise['date']} в {notise['time']}"

    @staticmethod
    def addReminderEcho(message):
        gpt_response = RequestEvent(message.text)
        try:
            parsed = ParseRequest(gpt_response)
        except ParseException:
            return Response("Извините, не могу вас правильно понять")
        except ValueError:
            return Response("Извините, не могу вас правильно понять")
        Bot.forward.Set(message.chat.id, Bot.addReminderEcho.__name__, parsed)
        notice = Bot.__prettyNotice(parsed)
        return Response(f"Добавить это напоминание?\n{notice}", Bot.addReminderAccept)

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
        text = '''Привет, я бот помощник, с моей помощью ты сможешь хранить свои заметки, и попросить меня напомнить тебе о чем\-то.
Основные команды:
/start \- начать работу
/gpt \- обратиться к сервису gpt4
/note или /add \- добавить заметку
/notice или /reminder \- добавить напоминание
/get \- получить список своих заметок
/del или /delete \- удалить заметку или напоминание
/help \- получить информацию о командах

Боту можно отвечать голосовыми сообщениями, или писать текстом.
Для работы с уведомлениями, лучше помимо напоминания, уточнять день и время в которые вы хотите получить уведомление.'''
        return Response(text)


    ''' list of bot commands 
        ( command function, list of command start key word )
        * only for single commands or root commands that starts echo *
    '''
    commands = [
        (startCommand.__func__, ['start']),
        (helloCommand.__func__, ['hello']),
        (gptCommand.__func__, ['gpt']),
        (addNoteCommand.__func__, ['note', 'add']),
        (getNoteCommand.__func__, ['get']),
        (deleteNoteCommand.__func__, ['del', 'delete']),
        (addReminderCommand.__func__, ['reminder', 'notice']),
        (helpCommand.__func__, ['help'])
    ]

    commands_dict = {
        'start': startCommand.__func__,
        'hello': helloCommand.__func__,
        'gpt': gptCommand.__func__,
        'note': addNoteCommand.__func__,
        'get': getNoteCommand.__func__,
        'delete': deleteNoteCommand.__func__,
        'notice': addReminderCommand.__func__,
        'help': helpCommand.__func__,
    }


if __name__ == "__main__":
    pass
