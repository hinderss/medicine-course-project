from flask import jsonify


class SuccessMeta(type):
    def __call__(cls, message, status_code=200, **kwargs):
        response = {'message': message}
        response.update(kwargs)
        return jsonify(response), status_code


class HttpSuccess(metaclass=SuccessMeta):
    pass
