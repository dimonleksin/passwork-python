class PassworkError(ValueError):
    """
    Base exception for Passwork client errors.
    Allows specifying an error code along with the message.
    """
    def __init__(self, message, code: str | None = None):
        super().__init__(message)
        self.code = code


class PassworkResponseError(ValueError):
    def __init__(self, message, url: str | None = None, method: str | None = None, code: str | None = None):
        self.message = message
        self.code = code
        self.url = url,
        self.method = method

    def __str__(self):
        return f"Message: {self.message} \nUrl: {self.url} \nMethod: {self.method} \nCode: {self.code}"
