from ChatGPT_Request import RequestEvent, ParseRequest


class Bot:
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


    ''' list of bot commands 
        ( command function, list of command start key word )
    '''
    commands = [
        (startCommand, ['start']),
        (helloCommand, ['hello'])
    ]


# testing func --------------

def testGptResponse() -> None:
    text = "Добавить напоминание о занятии 24 апреля в 12 часов дня"
    response = RequestEvent(text)
    print(f"'{response}'")


def testResponseParse() -> None:
    responses = [
        'дата: 24.04.2023\nвремя: 12:00\nсобытие: Занятие',
        'дата: %D.%M.%Y \nвремя: %H:%M \nсобытие: Занятие',
        'Событие: занятие  \nДата: 24.04.2024  \nВремя: 12:00'
        ]

    for resp in responses:
        print("source:", resp)
        data = ParseRequest(resp)
        print("\nparsed:")

        if data == -1:
            print("invalid data")
            continue

        for key in data.keys():
            print(f'key: {key}, value: "{data[key]}"')
        print("-------------")
    


if __name__ == "__main__":
    testResponseParse()

    
