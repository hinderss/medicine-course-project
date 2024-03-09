# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import DataRequired, Length, EqualTo#, Email


# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     submit = SubmitField('Login')

# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Sign Up')


# class DoctorRegistrationForm(FlaskForm):
#     surname = StringField('Фамилия', validators=[DataRequired()])
#     firstname = StringField('Имя', validators=[DataRequired()])
#     patronymic = StringField('Отчество', validators=[DataRequired()])
#     dob = StringField('Дата рождения: dd.mm.yy', validators=[DataRequired()])
#     education = StringField('Образование', validators=[DataRequired()])
#     workplace = StringField('Место работы', validators=[DataRequired()])
#     medical_practice_profile = StringField('Профиль врачебной практики', validators=[DataRequired()])
#     phone = StringField('Номер телефона', validators=[DataRequired()])
#     email = StringField('Адресс электронной почты', validators=[DataRequired(), Email()])
#     password = PasswordField('Пароль', validators=[DataRequired()])
#     submit = SubmitField('Зарегистрироваться')