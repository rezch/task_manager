from g4f.client import Client
#from g4f.client import *


def Request_Event(appender: str) -> str:
    initializer = "Сформируй текст в фоме: 1)дата начала: ,2)короткий текст-напоминание связанный с событием, 3)время напоминания в дате. Если ты не знаешь каких-то данных, то ставь -"


    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": initializer + appender}]
    )

    return response.choices[0].message.content

