from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from geopy.exc import GeocoderUnavailable
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import SelectField, RadioField
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.simple import FileField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, InputRequired, Optional, ValidationError
from app.validators import Phone, FutureDateValidator, FutureTimeValidator, PastDateValidator, get_coordinates


class LoginForm(FlaskForm):
    username = StringField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class DoctorForm(FlaskForm):
    firstname = StringField('Имя', validators=[
        DataRequired(message="Введите ваше имя")])
    surname = StringField('Фамилия', validators=[
        DataRequired(message="Введите вашу фамилию")])
    patronymic = StringField('Отчество', validators=[
        DataRequired(message="Введите ваше отчество")])
    dob = DateField('Дата рождения: дд.мм.гггг', validators=[
        DataRequired(message="Введите вашу дату рождения"),
        PastDateValidator(message="Дата рождения должна быть в прошлом.")])
    education = StringField('Образование', validators=[
        DataRequired(message="Введите ваше образование")])
    workplace = StringField('Место работы', validators=[
        DataRequired(message="Введите ваше место работы")])
    city = StringField('Город места работы', validators=[
        DataRequired(message="Введите город, где находится ваше место работы")])
    street = StringField('Улица места работы', validators=[
        DataRequired(message="Введите улицу, где находится ваше место работы")])
    building = StringField('Номер дома места работы', validators=[
        DataRequired(message="Введите номер дома, где находится ваше место работы")])
    practice_profile = StringField('Профиль врачебной практики', validators=[
        DataRequired(message="Введите ваш профиль врачебной практики")])
    phone = StringField('Номер телефона', validators=[
        DataRequired(message="Введите ваш номер телефона"),
        Phone(message="Неправильный формат номера телефона.")])
    email = StringField('Адрес электронной почты', validators=[
        DataRequired(message="Введите ваш адрес электронной почты"),
        Email(message="Неправильный формат адреса электронной почты")])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Введите ваш пароль"),
        Length(min=6, message="Пароль должен содержать как минимум 6 символов")])
    photo = FileField('Фотография', validators=[
        FileRequired(message="Загрузите вашу фотографию"),
        FileAllowed(['jpg', 'jpeg', 'png'], message="Разрешены только файлы с расширениями .jpg, .jpeg, .png")])

    latitude = HiddenField()
    longitude = HiddenField()

    submit = SubmitField('Зарегистрироваться')

    def validate(self, extra_validators=None):
        rv = super().validate()
        if not rv:
            return False

        try:
            lat, lon = get_coordinates(self.city.data, self.street.data, self.building.data)
            self.latitude.data = str(lat)
            self.longitude.data = str(lon)
            return True
        except ValueError:
            self.city.errors.append("Адрес не распознан. Уточните город, улицу и номер дома.")
        except GeocoderUnavailable:
            self.city.errors.append("Сервис геолокации недоступен. Попробуйте позже.")
        return False


class PatientForm(FlaskForm):
    firstname = StringField('Имя', validators=[
        DataRequired(message="Введите ваше имя")])
    surname = StringField('Фамилия', validators=[
        DataRequired(message="Введите вашу фамилию")])
    dob = DateField('Дата рождения: дд.мм.гггг', validators=[
        DataRequired(message="Введите вашу дату рождения"),
        PastDateValidator(message="Дата рождения должна быть в прошлом.")])
    CHOICES = [('', 'Выберите регион'), ('BY', 'BY'), ('RU', 'RU'), ('KZ', 'KZ')]
    region = SelectField('Регион', choices=CHOICES, validators=[
        DataRequired(message="Выберите ваш регион")])
    phone = StringField('Номер телефона', validators=[
        DataRequired(message="Введите ваш номер телефона"),
        Phone(message="Неправильный формат номера телефона.")])
    email = StringField('Адрес электронной почты', validators=[
        DataRequired(message="Введите ваш адрес электронной почты"),
        Email(message="Неправильный формат адреса электронной почты")])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Введите ваш пароль"),
        Length(min=6, message="Пароль должен содержать как минимум 6 символов")])
    photo = FileField('Фотография', validators=[
        FileRequired(message="Загрузите вашу фотографию"),
        FileAllowed(['jpg', 'jpeg', 'png'], message="Разрешены только файлы с расширениями .jpg, .jpeg, .png")])
    submit = SubmitField('Зарегистрироваться')


class MedicalCardForm(FlaskForm):
    surname = StringField('Фамилия', validators=[
        DataRequired()])
    firstname = StringField('Имя', validators=[
        DataRequired()])
    patronymic = StringField('Отчество')
    gender = RadioField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')])
    dob = DateField('Дата рождения: дд.мм.гггг', validators=[
        DataRequired(),
        PastDateValidator(message="Дата рождения должна быть в прошлом.")
    ])
    passport = StringField('Личный Номер паспорта')
    family = StringField('Семейное положение')
    document_type = StringField('Документ')
    document_serial = StringField('Серия документа')
    document_number = StringField('Номер документа')
    document_authority = StringField('Кем выдан')
    document_issue_date = DateField('Дата выдачи: дд.мм.гггг')
    region = StringField('Область')
    city = StringField('Населенный пункт')
    street = StringField('Улица/Переулок/Проезд')
    house = StringField('Дом')
    building = StringField('Корпус')
    entrance = StringField('Подъезд')
    apartment = StringField('Квартира')
    home_phone = StringField('Домашний телефон' 
                             ''', validators=[Phone(message="Неправильный формат номера телефона.")]'''
                             )
    registration_region = StringField('Область регистрации')
    registration_city = StringField('Населенный пункт регистрации')
    registration_street = StringField('Улица/Переулок/Проезд регистрации')
    registration_house = StringField('Дом регистрации')
    registration_building = StringField('Корпус регистрации')
    registration_entrance = StringField('Подъезд регистрации')
    registration_apartment = StringField('Квартира регистрации')
    insurance_serial = StringField('Серия страхового полиса')
    insurance_number = StringField('Номер страхового полиса')
    disability = StringField('Инвалидность')
    disability_group = StringField('Группа инвалидности')
    benefit_document = StringField('Документ на льготное обслуживание')
    payment_type = StringField('Вид оплаты')
    allergic_history = StringField('Аллергический анамнез')
    medication_intolerance = StringField('Лекарственная непереносимость')
    blood_group = StringField('Группа крови')
    rhesus = StringField('Резус')
    blood_belongs = StringField('Принадлежность крови')
    vaccine_reactions = StringField('Реакции на прививки')
    blood_transfusion = StringField('Переливание крови')
    surgical_intervention = StringField('Хирургическое вмешательство')
    previous_infectious_diseases = TextAreaField('Перенесенные инфекционные заболевания')
    submit = SubmitField('Сохранить')


class AppointmentForm(FlaskForm):
    date = StringField('Дата', validators=[
        InputRequired()])
    doctor_id = StringField('doctor id', validators=[
        DataRequired()])
    time = SelectField('Время записи', choices=[], validate_choice=False, validators=[
        DataRequired()])
    appointment_details = TextAreaField('Детали записи')
    submit = SubmitField('Записаться')


class CreateAppointmentForm(FlaskForm):
    date = DateField('Дата: дд.мм.гггг', validators=[
        DataRequired(),
        FutureDateValidator()])
    time = TimeField('Время: ', validators=[
        DataRequired(),
        FutureTimeValidator()])
    submit = SubmitField('Создать окно записи')


class ScheduleTimeValidator:
    def __init__(self, bool_field, message=None):
        if not message:
            message = 'Time required'
        self.message = message
        self.bool_field = bool_field

    def __call__(self, form, field):
        if self.bool_field.data:
            if not field.data:
                raise ValidationError(self.message)
        else:
            field.validators = []


class DoctorScheduleForm(FlaskForm):
    monday_check = BooleanField('Понедельник')
    monday_start_time = TimeField('C', validators=[Optional()])
    monday_end_time = TimeField('До', validators=[Optional()])
    monday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    tuesday_check = BooleanField('Вторник')
    tuesday_start_time = TimeField('C', validators=[Optional()])
    tuesday_end_time = TimeField('До', validators=[Optional()])
    tuesday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    wednesday_check = BooleanField('Среда')
    wednesday_start_time = TimeField('C', validators=[Optional()])
    wednesday_end_time = TimeField('До', validators=[Optional()])
    wednesday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    thursday_check = BooleanField('Четверг')
    thursday_start_time = TimeField('C', validators=[Optional()])
    thursday_end_time = TimeField('До', validators=[Optional()])
    thursday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    friday_check = BooleanField('Пятница')
    friday_start_time = TimeField('C', validators=[Optional()])
    friday_end_time = TimeField('До', validators=[Optional()])
    friday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    saturday_check = BooleanField('Суббота')
    saturday_start_time = TimeField('C')
    saturday_end_time = TimeField('До', validators=[Optional()])
    saturday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    sunday_check = BooleanField('Воскресенье')
    sunday_start_time = TimeField('C', validators=[Optional()])
    sunday_end_time = TimeField('До')
    sunday_duration = IntegerField('продолжительность(мин)', validators=[Optional()])

    submit = SubmitField('Сохранить')


class QueryForm(FlaskForm):
    query = StringField("Поиск", validators=[DataRequired(message="Введите поисковой запрос")])

    submit = SubmitField('Поиск')


RecommendationForm = QueryForm


class NavigationForm(QueryForm):
    LANGUAGES = [('rus', 'Русский'), ('eng', 'Английский')]
    language = SelectField('Язык', choices=LANGUAGES, validators=[Optional()])


class CommonBloodForm(FlaskForm):
    erythrocytes = FloatField(
        "Эритроциты",
        validators=[DataRequired(message="Введите эритроциты")],
        render_kw={"type": "number", "step": 0.01},
    )
    leukocytes = FloatField(
        "Лейкоциты",
        validators=[DataRequired(message="Введите лейкоциты")],
        render_kw={"type": "number", "step": 0.01},
    )
    platelets = FloatField(
        "Тромбоциты",
        validators=[DataRequired(message="Введите тромбоциты")],
        render_kw={"type": "number", "step": 0.01},
    )
    submit = SubmitField('Анализ')


class MicronutrientsBloodForm(FlaskForm):
    calcium = FloatField(
        "Кальций",
        validators=[DataRequired(message="Введите кальций")],
        render_kw={"type": "number", "step": 0.01},
    )
    magnium = FloatField(
        "Магний",
        validators=[DataRequired(message="Введите магний")],
        render_kw={"type": "number", "step": 0.01},
    )
    ferrum = FloatField(
        "Железо",
        validators=[DataRequired(message="Введите железо")],
        render_kw={"type": "number", "step": 0.01},
    )
    submit = SubmitField('Анализ')


class VitaminBloodForm(FlaskForm):
    vitamin_e = FloatField(
        "Витамин E",
        validators=[DataRequired(message="Введите значение витамина E")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_d = FloatField(
        "Витамин D",
        validators=[DataRequired(message="Введите значение витамина D")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_k = FloatField(
        "Витамин K",
        validators=[DataRequired(message="Введите значение витамина K")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_c = FloatField(
        "Витамин C",
        validators=[DataRequired(message="Введите значение витамина C")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_b1 = FloatField(
        "Витамин B1",
        validators=[DataRequired(message="Введите значение витамина B1")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_b2 = FloatField(
        "Витамин B2",
        validators=[DataRequired(message="Введите значение витамина B2")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_b9 = FloatField(
        "Витамин B9",
        validators=[DataRequired(message="Введите значение витамина B9")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_b12 = FloatField(
        "Витамин B12",
        validators=[DataRequired(message="Введите значение витамина B12")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_a = FloatField(
        "Витамин A",
        validators=[DataRequired(message="Введите значение витамина A")],
        render_kw={"type": "number", "step": 0.01},
    )
    vitamin_b6 = FloatField(
        "Витамин B6",
        validators=[DataRequired(message="Введите значение витамина B6")],
        render_kw={"type": "number", "step": 0.01},
    )
    submit = SubmitField('Анализ')


class HormonesBloodForm(FlaskForm):
    tsh = FloatField(
        "Тиреотропный гормон", 
        validators=[DataRequired(message="Введите значение")],
        render_kw={"type": "number", "step": 0.01},
    )
    fsh = FloatField(
        "Фолликулостимулирующий гормон", 
        validators=[DataRequired(message="Введите значение")],
        render_kw={"type": "number", "step": 0.01},
    )
    lh = FloatField(
        "Лютеинизирующий гормон", 
         validators=[DataRequired(message="Введите значение")],
         render_kw={"type": "number", "step": 0.01},
    )
    submit = SubmitField('Анализ')
