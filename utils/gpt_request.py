from g4f.client import Client
from g4f.models import gpt_4, gpt_35_turbo
from datetime import datetime
from translatepy import Translator


REQUEST_PROMPT = 'Представь что ты помошник в напоминаниях о событиях. Вот текст события: {}.' \
                  'Учитывая, что сегодня {:%H:%M, %d-%m-%Y}, Найди в нем дату, ' \
                  'в формате "дата: %D.%M.%Y", и время, в формате "время: %H:%M", в которое ты должен напомнить об ' \
                  'этом событии, а также информацию об этом событии. И ответь мне в формате "событие - ", "дата - ", ' \
                  '"время - ". Если информации о дате или времени нет, то воспользуйся сегодняшним временем и датой'

MODEL = gpt_35_turbo
TIMEOUT = 60 # sec
ATTEMPTS = 3


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


def ChangeAttempts(attempts: str) -> bool:
    global ATTEMPTS
    try:
        attempts = int(attempts)
    except ValueError:
        return False
    if 0 > attempts or attempts > 10:
        return False
    ATTEMPTS = attempts
    return True


def GetGlobalVars() -> dict:
    global MODEL, TIMEOUT, ATTEMPTS
    return {
            'model': MODEL,
            'timeout': TIMEOUT,
            'attempts': ATTEMPTS,
            }


def RawRequestEvent(appender: str) -> str:
    global MODEL, TIMEOUT

    print(TIMEOUT)
    client = Client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role":
                "user", "content": appender
        }],
        timeout=TIMEOUT,
    )

    response = response.choices[0].message.content

    translator = Translator()
    if str(translator.language(response).result) == 'zho':
        response = translator.translate(response, 'Russian').result

    print("Gpt response: ", response)
    return response


def RawGptRequest(appender: str) -> str:
    global ATTEMPTS
    for _ in range(ATTEMPTS):
        try:
            response = RawRequestEvent(appender)
            if response == 'Текущая область была использована в тот день, попробуйте изменить сетевую среду':
                raise ValueError
            return response
        except Exception as e:
            print(f'Gpt error: {e}')
    return 'Извините, сервис gpt4 временно не доступен'


def RequestEvent(appender: str) -> str:
    """ returns response of parsed text from user by gpt4 """
    global MODEL, TIMEOUT

    print(f'Request (timeout: {TIMEOUT}) for {MODEL}: {appender}')

    initializer = REQUEST_PROMPT.format(appender, datetime.now())

    # sending request to gpt4
    print(TIMEOUT)
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

    if 'None' in response or 'none' in response:
        return {'bad_value': f"Не заполнена информация о конкретной дате и времени напоминания"}

    result = {
        'date': '',
        'time': '',
        'info': ''
    }

    # dict with key word for parsing
    key_words = {
        'дата': 'date',
        'время': 'time',
        'событие': 'info',
        '日期': 'date',
        '时间': 'time',
        '事件': 'info'
    }

    # response preproccessing
    response = response.split('\n')
    response = [line.lower().split('-') for line in response]

    print(response)

    for line in response:
        key = line[0].strip()
        if key in key_words:
            result[key_words[key]] = line[1].strip()

    for key, value in result.items():
        if 'None' in value or 'none' in value:
            return {'bad_value': f"Не заполнена информация о {list(key_words.keys())[list(key_words.values()).index(key)]}"}

    try:
        datetime.strptime(result['date'] + ' ' + result['time'], '%d.%m.%Y %H:%M')
    except ValueError:
        raise ParseException()

    result['info'] = Translator().translate(result['info'], 'Russian').result

    return result


def Request(message):
    for _ in range(ATTEMPTS):
        response = RequestEvent(message)
        try:
            result = ParseRequest(response)
        except ParseException:
            continue
        return result
    return None


if __name__ == "__main__":
    print(Translator().translate("关于今天晚上的电话", 'Chinese'))
