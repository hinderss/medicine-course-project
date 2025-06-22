import re
from enum import Enum


class Regions(Enum):
    BY = 'BY'
    RU = 'RU'
    KZ = 'KZ'

class Validator:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    def __init__(self):
        pass

    class Validator:
        def __init__(self):
            pass

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Validator.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_name(name):
        # Проверка имени, фамилии, отчества
        # Допускаются только буквы и пробелы
        if re.match("^[A-Za-zА-Яа-яЁё\s]+$", name):
            return None
        else:
            return "Некорректное имя. Допускаются только буквы и пробелы."

    @staticmethod
    def validate_date(date):
        # Проверка даты в формате dd.mm.yyyy
        if re.match("^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", date):
            return None
        else:
            return "Некорректная дата. Формат должен быть dd.mm.yyyy."

    @staticmethod
    def validate_region(region):
        # Validate region
        if region in Regions.__members__:
            return None
        else:
            return "Invalid region."

    @staticmethod
    def validate_phone_number(phone_number):
        if phone_number == '':
            return None
        # Проверка номера телефона
        # Позволяется формат +71234567890 или 71234567890
        if re.match("^\+?[0-9]{12}$", phone_number):
            return None
        else:
            return "Некорректный номер телефона."

    @staticmethod
    def validate_email(email):
        # Проверка адреса электронной почты
        if re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return None
        else:
            return "Некорректный адрес электронной почты."

    @staticmethod
    def validate_city(city):
        return None

    @staticmethod
    def validate_password(password):
        return None
        # Проверка пароля
        # Минимум 8 символов, должен содержать хотя бы одну заглавную букву,
        # одну строчную букву, одну цифру и один спецсимвол
        if re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            return None
        else:
            return "Некорректный пароль. Пароль должен содержать минимум 8 символов, хотя бы одну заглавную букву, одну строчную букву, одну цифру и один спецсимвол."

    @staticmethod
    def validate_doctor(surname, firstname, patronymic, dob, phone, email, password, **kwargs):
        errors = ""

        surname_error = Validator.validate_name(surname)
        if surname_error:
            errors += f"{surname_error}<br>"

        firstname_error = Validator.validate_name(firstname)
        if firstname_error:
            errors += f"{firstname_error}<br>"

        patronymic_error = Validator.validate_name(patronymic)
        if patronymic_error:
            errors += f"{patronymic_error}<br>"

        dob_error = Validator.validate_date(dob)
        if dob_error:
            errors += f"{dob_error}<br>"

        phone_error = Validator.validate_phone_number(phone)
        if phone_error:
            errors += f"{phone_error}<br>"

        email_error = Validator.validate_email(email)
        if email_error:
            errors += f"{email_error}<br>"

        password_error = Validator.validate_password(password)
        if password_error:
            errors += f"{password_error}<br>"

        return errors

    @staticmethod
    def validate_patient(surname, firstname, dob, region, phone, email, password):
        errors = ""

        surname_error = Validator.validate_name(surname)
        if surname_error:
            errors += f"{surname_error}<br>"

        firstname_error = Validator.validate_name(firstname)
        if firstname_error:
            errors += f"{firstname_error}<br>"

        dob_error = Validator.validate_date(dob)
        if dob_error:
            errors += f"{dob_error}<br>"

        region_error = Validator.validate_region(region)
        if region_error:
            errors += f"{region_error}<br>"

        phone_error = Validator.validate_phone_number(phone)
        if phone_error:
            errors += f"{phone_error}<br>"

        email_error = Validator.validate_email(email)
        if email_error:
            errors += f"{email_error}<br>"

        password_error = Validator.validate_password(password)
        if password_error:
            errors += f"{password_error}<br>"

        return errors

    @staticmethod
    def validate_med_card(surname, firstname, dob, region, home_phone, document_issue_date, **kwargs):
        errors = ""

        surname_error = Validator.validate_name(surname)
        if surname_error:
            errors += f"{surname_error}<br>"

        firstname_error = Validator.validate_name(firstname)
        if firstname_error:
            errors += f"{firstname_error}<br>"

        dob_error = Validator.validate_date(dob)
        if dob_error:
            errors += f"{dob_error}<br>"

        region_error = Validator.validate_city(region)
        if region_error:
            errors += f"{region_error}<br>"

        phone_error = Validator.validate_phone_number(home_phone)
        if phone_error:
            errors += f"{phone_error}<br>"

        document_issue_error = Validator.validate_date(document_issue_date)
        if document_issue_error:
            errors += f"{document_issue_error}<br>"

        return errors



# Пример использования класса Validator
validator = Validator()

# Проверка имени
print(validator.validate_name("John Doe"))  # True
print(validator.validate_name("John123"))  # False

# Проверка даты
print(validator.validate_date("01.01.22"))  # True
print(validator.validate_date("32.01.22"))  # False

# Проверка номера телефона
print(validator.validate_phone_number("+71234567890"))  # True
print(validator.validate_phone_number("71234567890"))  # True
print(validator.validate_phone_number("1234567890"))  # False

# Проверка адреса электронной почты
print(validator.validate_email("example@example.com"))  # True
print(validator.validate_email("example.com"))  # False

# Проверка пароля
print(validator.validate_password("Passw0rd!"))  # True
print(validator.validate_password("password123"))  # False
