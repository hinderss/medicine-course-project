import re
from datetime import datetime

from geopy import Nominatim
from wtforms.validators import ValidationError

RE_PHONE = (r"^((8|\+374|\+994|\+995|\+375|\+7|\+380|\+38|\+996|\+998|\+993)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]"
            r"?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$")


class Phone(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Неправильный номер телефона'
        self.message = message

    def __call__(self, form, field):
        phone_number = field.data
        if not re.match(RE_PHONE, phone_number):
            raise ValidationError(self.message)


class PastDateValidator:
    def __init__(self, message=None):
        if not message:
            message = 'Дата должна быть в прошлом.'
        self.message = message

    def __call__(self, form, field):
        today = datetime.now().date()
        if field.data > today:
            raise ValidationError(self.message)


class FutureDateValidator:
    def __init__(self, message=None):
        if not message:
            message = 'Дата должна быть в будущем.'
        self.message = message

    def __call__(self, form, field):
        today = datetime.now().date()
        if field.data < today:
            raise ValidationError(self.message)


class FutureTimeValidator:
    def __init__(self, message=None):
        if not message:
            message = 'Время должно быть в будущем.'
        self.message = message

    def __call__(self, form, field):
        selected_date = form.date.data
        selected_time = field.data
        selected_datetime = datetime.combine(selected_date, selected_time)

        if selected_datetime <= datetime.now():
            raise ValidationError(self.message)


def get_coordinates(city, street, building):
    geolocator = Nominatim(user_agent="doctor_registration_app")
    address = f"{city}, {street}, {building}"
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError("Координаты не найдены по введённому адресу.")
