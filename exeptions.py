class StatusCodeError(Exception):
    """Ошибка возникает, если status_code != 200."""

    pass


class ApiAnswerError(Exception):
    """Любые другие сбои при запросе к эндпоинту."""

    pass


class GetTokenFailed(Exception):
    """Ошибка, если нет доступа к переменным окружения."""

    pass


class SendMessageError(Exception):
    """Ошибка при отправке сообщения."""

    pass
