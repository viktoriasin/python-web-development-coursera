class ApiError(Exception):

    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return str(self.status)
        else:
            return f"{self.status} ({self.message})"


class RequestApiError(Exception):

    def __init__(self, base_exception=None):
        self.base_exception = base_exception

    def __str__(self):
        if self.base_exception:
            return str(self.base_exception)

        return "An unknown error occurred."
