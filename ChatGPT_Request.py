from g4f.client import Client

REQUEST_MESSAGE = 'Представь что ты помошник в напоминаниях о событиях. Вот текст события: {}. Найди в нем дату, ' \
                  'в формате "дата: %D.%M.%Y", и время, в формате "время: %H:%M", в которое ты должен напомнить об ' \
                  'этом событии, а также информацию об этом событии. И ответь мне в формате "событие - ", "дата - ", ' \
                  '"время - " '


class ParseException(Exception):
    def __init__(self, message=None):
        if message is None:
            message = ''
        self._message = message

    def __str__(self):
        return f"Voice message parser error: {self._message}"


def RequestEvent(appender: str) -> str:
    """ returns response of parsed text from user by gpt4 """

    print("Request for gpt: ", appender)

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

    print("Gpt response: ", response.choices[0].message.content)

    return response.choices[0].message.content


def ParseRequest(response: str) -> dict:
    """ returns dict with parsed gpt response
        if response is invalid, return -1
    """

    result = {
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
    response = [line.lower().split('-') for line in response]

    print(response)
    if len(response) != 3:
        raise ParseException()

    for line in response:
        key = line[0].strip()
        if key not in key_words:
            raise ParseException()
        result[key_words[key]] = line[1].strip()

    return result


if __name__ == "__main__":
    resp = '''событие - занятие
дата - 26.5.2022
время - 18:00'''
    res = ParseRequest(resp)
    print(res)
