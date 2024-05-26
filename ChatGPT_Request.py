from g4f.client import Client
from g4f.models import gpt_4, gpt_35_turbo

REQUEST_MESSAGE = 'Представь что ты помошник в напоминаниях о событиях. Вот текст события: {}. Найди в нем дату, ' \
                  'в формате "дата: %D.%M.%Y", и время, в формате "время: %H:%M", в которое ты должен напомнить об ' \
                  'этом событии, а также информацию об этом событии. И ответь мне в формате "событие - ", "дата - ", ' \
                  '"время - " '

MODEL = gpt_35_turbo
TIMEOUT = 60  # sec


class ParseException(Exception):
    def __init__(self, message=None):
        if message is None:
            message = ''
        self._message = message

    def __str__(self):
        return f"Voice message parser error: {self._message}"


def ChangeModel(new_model: str) -> bool:
    global MODEL

    models = {
        'gpt-3.5t': gpt_35_turbo,
        'gpt-4': gpt_4,
    }

    if new_model not in models:
        return False

    MODEL = models[new_model]
    return True


def ChangeTimeout(tv: str) -> bool:
    global TIMEOUT

    try:
        tv = int(tv)
        if tv < 5 or tv > 600:
            raise ValueError
    except ValueError:
        return False

    TIMEOUT = tv
    return True

def GetGlobalVars() -> dict:
    global MODEL, TIMEOUT
    return {
            'model': MODEL,
            'timeout': TIMEOUT,
            }


def RequestEvent(appender: str) -> str:
    """ returns response of parsed text from user by gpt4 """
    global MODEL, TIMEOUT

    print(f'Request (timeout: {TIMEOUT}) for {MODEL}: {appender}')

    initializer = REQUEST_MESSAGE.format(appender)
    print(TIMEOUT)

    # sending request to gpt4
    client = Client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role":
                "user", "content": initializer
        }],
        timeout=TIMEOUT,
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
