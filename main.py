from ChatGPT_Request import RequestEvent, ParseRequest


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


class Request:
    def __init__(self, message, echo=None):
        self.message = message
        self.echo = echo

    def __iter__(self):
        yield from [self.message, self.echo]

    def __str__(self):
        return str(self.message)


class Bot:
    """ bot commands
        args: message
        return: answer message
                or
                (answer message, echo command)
    """

    __instance = None
    forward = UserResponse()

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls

    @staticmethod
    def startCommand(message):
        """ start command """
        return Request("Start")

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
        return Request(result)

    @staticmethod
    def echoCommand(message):
        return Request(message.text)

    @staticmethod
    def testEchoCommand(message):
        return Request("--", Bot.echoCommand)

    @staticmethod
    def gptEchoCommand(message):
        try:
            response = RequestEvent(message.text)
        except:
            response = 'Извините, сервис gpt4 временно не доступен'
        return Request(response)

    @staticmethod
    def gptCommand(message):
        """ request to gpt """
        return Request("Какой у вас вопрос?", Bot.gptEchoCommand)

    """
    example of forwarding data between echo functions
    """
    @staticmethod
    def addNoteCommand(message):
        """ add note start command """
        return Request("Что вы хотите записать?", Bot.addNoteGetText)

    @staticmethod
    def addNoteGetText(message):
        """ getting text to add note """
        print('dump:', message.chat.id, 'addNoteGetText', message.text)
        Bot.forward.Set(message.chat.id, 'addNoteGetText', message.text)
        return Request(message.text)

    @staticmethod
    def getNoteText(message):
        res = Bot.forward.Get(message.chat.id, 'addNoteGetText') 
        return Request(res)
    # ----------------------

    ''' list of bot commands 
        ( command function, list of command start key word )
        * only for single commands or root commands that starts echo *
    '''
    commands = [
        (startCommand.__func__, ['start']),
        (helloCommand.__func__, ['hello']),
        (testEchoCommand.__func__, ['echo']),
        (gptCommand.__func__, ['gpt']),
        (addNoteCommand.__func__, ['note']),
        (getNoteText.__func__, ['get']),
    ]


if __name__ == "__main__":
    pass
