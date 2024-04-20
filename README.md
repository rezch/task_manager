# task-manager tgbot

# Ключевые команды бота для пользователя
- `/event` - Добавить новое событие.
  -После идёт заполнения текст, время начала, время конца.
- `/note` - Добавить новую задачу.
  -После идёт заполнения текст, время напоминания.
- `/delete` - Удалить задачу.
- `/edit` - Редактировать существующую задачу.
- `/complete` - Пометить задачу как завершенную.
- `/remind` - Напомнить о задаче в определенное время.

_* План  если у задач будет Номер, Название, Дата создания, Дата завершения, то нужно дать пользователю возможность редактировать сообщение по любому из этих пунктов (Смотри /view) *_

*В зависимости от того, как мы хотим перечислять уже существующие задачи. Также нужно понимать, по какому параметру отображать задачу. Можно сразу по нескольким:*
- */view [номер задачи]* - Пользователь может указать номер задачи для просмотра ее деталей.
- */view [название задачи]* - Пользователь может указать название задачи для просмотра ее деталей.
- */view [дата создания]* - Пользователь может указать дату создания задачи для просмотра ее деталей.
- */view [дата окончания/начала]* - Пользователь может указать дату окончания/начала события (окончания для note) для просмотра ее деталей.


- `/view` - Показать список всех задач.
- `/help` - Получить помощь и список доступных команд.
- `/stats` - Получить персональную статистику.

# Дополнительные команды
Проблема данной команды очевидна. Нужно ли нам вообще подвязывать гугл календарь? Технически это очень и очень сложно, так что на обсуждение
- `/link ` - Привязать гугл аккаунт

