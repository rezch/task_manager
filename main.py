from ChatGPT_Request import RequestEvent, ParseRequest


class Bot:
    """ bot commands
        args: message
        return: answer message
                or
                (answer message, echo command)
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls

    @staticmethod
    def startCommand(message):
        """ start command """
        return "Start"

    @staticmethod
    def helloCommand(message):
        """ hello command """
        result = 'Hello '
        if message.from_user.first_name is None and message.from_user.last_name is None:
            return result + message.from_user.username
        if message.from_user.first_name is not None:
            result += message.from_user.first_name
        if message.from_user.last_name is not None:
            result += message.from_user.last_name
        return result

    @staticmethod
    def echoCommand(message):
        return message.text

    @staticmethod
    def testEchoCommand(message):
        return "--", Bot.echoCommand

    @staticmethod
    def gptEchoCommand(message):
        try:
            response = RequestEvent(message.text)
        except:
            response = 'Извините, сервис gpt4 временно не доступен'
        return response

    @staticmethod
    def gptCommand(message):
        """ request to gpt """
        return "Какой у вас вопрос?", Bot.gptEchoCommand

    ''' list of bot commands 
        ( command function, list of command start key word )
        * only for single commands or root commands that starts echo *
    '''
    commands = [
        (startCommand.__func__, ['start']),
        (helloCommand.__func__, ['hello']),
        (testEchoCommand.__func__, ['echo']),
    ]


if __name__ == "__main__":
    pass
