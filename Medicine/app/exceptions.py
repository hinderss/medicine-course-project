class HttpException(Exception):
    def __init__(self, status_code=None, message=None):
        self.status_code = status_code or 500
        self.message = message or "An HTTP error occurred"
        super().__init__(self.message)


class Http400(HttpException):
    def __init__(self, status_code=None, message=None):
        super().__init__(status_code or 400, message or "Bad request")


class Http403(Http400):
    def __init__(self, message=None):
        super().__init__(403, message or "Forbidden")


class Http404(Http400):
    def __init__(self, message=None):
        super().__init__(404, message or "Not found")


class HttpJson(HttpException):
    def to_dict(self):
        return {'error': self.message or "An HTTP error occurred"}


class HttpJson404(HttpJson):
    def __init__(self, message=None):
        super().__init__(404, message or "Not found")


class HttpJson400(HttpJson):
    def __init__(self, message=None):
        super().__init__(400, message or "Bad request")


class HttpJson403(HttpJson):
    def __init__(self, message=None):
        super().__init__(403, message or "Forbidden")


class HttpJson409(HttpJson):
    def __init__(self, message=None):
        super().__init__(409, message or "Conflict")
