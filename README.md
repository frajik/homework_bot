# TelegramBot 

## Описание:
 **Bot** работает с API Яндекс.Практикума, отслеживает статус домашней работы, отправленной на ревью - при изменении статуса присылает соответствующее сообщение.

## Используемые технологии:
- [Python 3.7](https://www.python.org/)
- [DRF](https://www.django-rest-framework.org/)
- [JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)


## Как запустить проект:
1. Клонируем репозиторий к себе на компьютер:
```
    git@github.com:frajik/homework_bot.git
```

2. Переходим в репозиторий:
```
    cd homework_bot
```

3. Создаем и активируем рабочее окружение:
```
    - python -m venv venv
    - source venv/scripts/activate
```

4. Устанавливаем зависимости из файла requirements.txt:
```
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt
```

5. В консоле импортируем токены для Яндекс.Практикум и для Телеграмм::
```
    - export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
    - export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
    - export CHAT_ID=<CHAT_ID>
```
Примечание. [Эндпоинт](https://practicum.yandex.ru/api/user_api/homework_statuses/) API Яндекс.Практикума, доступ к нему возможен только по токену, который можно получить [ТУТ](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)

6. Запускаем бота:
```
    - python homework.py
```
## Принцип работы:
- Ревьюер может присвоить домашней работе 3 статуса:
  1.работа принята на проверку;
  2.работа возвращена для исправления ошибок;
  3.работа принята;
- Бот каждые 10 минут проверяет статус домашней работы;
- Если статус работы поменялся - бот присылает соответствующее сообщение.

###Автор: 
**Матвейчук Дмитрий**
