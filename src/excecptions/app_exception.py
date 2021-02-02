class AppException(Exception):
    def __init__(self, error, http_code):
        # Now for your custom code...
        self.error = error
        self.http_code = http_code


class BadRequestException(AppException):
    def __init__(self, error=None):
        super().__init__(error, 400)


class NotFoundException(AppException):
    def __init__(self, error=None):
        super().__init__(error, 404)


class ServerException(AppException):
    def __init__(self, error=None):
        super().__init__(error, 500)
