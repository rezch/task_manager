from g4f.client import Client


REQUEST_MESSAGE = 'Представь что ты помошник в напоминаниях о событиях. Вот текст события: {}. Найди в нем дату, в формате "дата: %D.%M.%Y", и время, в формате "время: %H:%M", в которое ты должен напомнить об этом событии, а также информацию об этом событии, в формате "событие: "'


def RequestEvent(appender: str) -> str:
    ''' returns response of parsed text from user by gpt4 '''

    initializer = REQUEST_MESSAGE.format(appender)

    # sending request to gpt4
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": 
            "user", "content": initializer
            }]
    )

    return response.choices[0].message.content


def ParseRequest(response: str) -> dict:
    ''' returns dict with parsed gpt response
        if response if invalid, return -1
    '''

    # result dict
    data = {
        'date': '',
        'time': '',
        'info': ''
    }

    # dict with key word for parsing
    key_words = {
        'дата': 'date',
        'время': 'time',
        'событие': 'info'
    }


    # response preproccessing
    response = response.split('\n')
    response = [line.lower().split(':') for line in response]

    if len(response) != 3:
        return -1

    # data parse    
    for line in response:
        if line[0] not in key_words:
            return -1
        data[key_words[line[0]]] = line[1].strip()

    return data 

