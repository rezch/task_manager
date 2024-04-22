from ChatGPT_Request import RequestEvent, ParseRequest


class Bot:
    ''' bot commands
        args: message
        return: answer message
                or
                (answer message, echo command)
    '''

    def startCommand(messege):
        ''' start command '''
        return "Start"

    def helloCommand(message):
        ''' hello command '''
        result = 'Hello '
        if message.from_user.first_name is None and message.from_user.last_name is None:
            return result + message.from_user.username
        if message.from_user.first_name is not None:
            result += message.from_user.first_name
        if message.from_user.last_name is not None:
            result += message.from_user.last_name
        return result

    def echoCommand(message):
        return "echo"

    def testEchoCommand(message):
        return ("--", Bot.echoCommand)


    ''' list of bot commands 
        ( command function, list of command start key word )
        * only for single commands or root commands that starts echo *
    '''
    commands = [
        (startCommand, ['start']),
        (helloCommand, ['hello']),
        (testEchoCommand, ['echo']),
    ]


if __name__ == "__main__":
    pass

    
