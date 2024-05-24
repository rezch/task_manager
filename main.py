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


class Bot:
    """ bot commands
        args: message
        return: Response(message, next_step(opt))
    """

    __instance = None
    forward = UserResponse()
    db = DB("data.json")

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls

    @staticmethod
    def startCommand(message):
        """ start command """
        return Response('Star.t')

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
        user_data = Bot.db.getUserData(message.from_user.id)
        if 'notes' not in user_data.keys():
            user_data['notes'] = []
        user_data['notes'].append(message.text)
        Bot.db.Dump()
        return Response("Заметка успешно добавлена")

    @staticmethod
    def __prettyNotes(message) -> str:
        """ convert user notes list to formatted string for response """
        user_data = Bot.db.getUserData(message.from_user.id)

        data = []
        if 'notes' in user_data.keys():
            data.extend(user_data['notes'])

        notes_ind = len(data)
        if 'notices' in user_data.keys() and user_data['notices'] != []:
            notices = []
            for notice in user_data['notices']:
                notices.append(Bot.__prettyNotice(notice))

            data.extend(notices)

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
        user_data = Bot.db.getUserData(message.from_user.id)
        try:
            note_id = int(note_id)
            if note_id > len(user_data['notes']) or note_id < 1:
                raise TypeError
        except TypeError:
            return Response('Номер заметки указан не верно')
        user_data['notes'].pop(note_id - 1)
        Bot.db.Dump()
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
            print("BAD GPT RESPONSE")
            return Response("Извините, не могу вас правильно понять")
        Bot.forward.Set(message.from_user.id, Bot.addReminderEcho.__name__, parsed)
        notice = Bot.__prettyNotice(parsed)
        return Response(f"Добавить это напоминание?\n{notice}", Bot.addReminderAccept)

    @staticmethod
    def addReminderAccept(message):
        response = str(message.text).lower()
        if response not in ['да', 'yes']:
            return Response('Напоминание не было добавлено')
        notice = Bot.forward.Get(message.from_user.id, Bot.addReminderEcho.__name__)
        user_data = Bot.db.getUserData(message.from_user.id)
        if 'notices' not in user_data.keys():
            user_data['notices'] = []
        user_data['notices'].append(notice)
        Bot.db.Dump()
        return Response('Напоминание успешно добавлено')

    @staticmethod
    def getReminderCommand(message):
        pass


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
    ]


if __name__ == "__main__":
    pass
