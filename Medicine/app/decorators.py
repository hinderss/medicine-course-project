from functools import wraps

from flask_login import current_user

from app.exceptions import Http403

from app import db


def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.patient:
            raise Http403("You are not authorized as patient to access this page.")
        return f(*args, **kwargs)
    return decorated_function


def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.doctor:
            raise Http403("You are not authorized as doctor to access this page.")
        return f(*args, **kwargs)
    return decorated_function


def transaction_atomic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e
        finally:
            db.session.close()
    return wrapper
