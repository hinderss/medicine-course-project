import os
from datetime import datetime

from sqlalchemy import cast, Date
from werkzeug.utils import secure_filename

from app.helpers import save_file
from app.validator import Validator
from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify, abort
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from app.forms import LoginForm, DoctorForm, PatientForm, MedicalCardForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'

    if current_user.is_authenticated:
        if current_user.patient:
            user = current_user.patient
        else:
            user = current_user.doctor
        name = user.firstname
        surname = user.surname
        return render_template(template, name=name, surname=surname)

    return render_template(template)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/medical_card', methods=['GET', 'POST'])
@login_required
def medical_card():
    template = 'medicalCard.html'
    form: MedicalCardForm
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    patient = current_user.patient
    if not patient:
        return "You are not authorized to access this page. Enter as patient"

    existing_med_card = MedicalCard.query.filter_by(patient_id=patient.id).first()
    if existing_med_card:
        form = MedicalCardForm(obj=existing_med_card)
    else:
        form = MedicalCardForm(surname=patient.surname,
                               firstname=patient.firstname,
                               dob=patient.dob)
    if form.validate_on_submit():
        if existing_med_card:
            form.populate_obj(existing_med_card)  # Заполняем объект медицинской карты данными из формы
        else:
            new_med_card = MedicalCard(patient_id=current_user.patient.id)  # Создаем новый объект медицинской карты
            form.populate_obj(new_med_card)  # Заполняем его данными из формы
            db.session.add(new_med_card)  # Добавляем в сессию базы данных для сохранения

        current_user.patient.surname = form.surname.data
        current_user.patient.firstname = form.firstname.data
        current_user.patient.dob = form.dob.data

        db.session.commit()

        return redirect(url_for('index'))
    return render_template(template, form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/doctors', methods=['GET'])
def get_doctors_by_specialty():
    specialty = request.args.get('specialty')

    if not specialty:
        return jsonify({'error': 'Специальность не указана'}), 400

    doctors = Doctor.query.filter_by(practice_profile=specialty).all()

    return jsonify([doctor.to_dict() for doctor in doctors])


# Маршрут для получения списка всех доступных в базе данных practice_profile
@app.route('/practice_profiles', methods=['GET'])
def get_practice_profiles():
    # Получаем список всех уникальных значений practice_profile из таблицы Doctor
    practice_profiles = Doctor.query.with_entities(Doctor.practice_profile).distinct().all()

    # Преобразуем список кортежей в список строк
    practice_profiles = [profile[0] for profile in practice_profiles]

    # Возвращаем список в формате JSON
    return jsonify({'practice_profiles': practice_profiles})


@app.route('/appointments/get_doctor_time')
def get_doctor_appointments():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')  # Получаем дату в формате строки
    if doctor_id and date_str:
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            # Преобразуем строку даты в объект datetime
            date = datetime.strptime(date_str, '%Y-%m-%d')
            print(date)
            print(cast(Appointment.appointment_date_time, Date))
            print(Appointment.appointment_date_time)
            # Фильтруем записи для указанного врача и даты
            appointments = Appointment.query.filter_by(doctor_id=doctor_id) \
                .filter(db.func.date(Appointment.appointment_date_time) == date.date()) \
                .filter(Appointment.patient_id.is_(None)) \
                .all()
            print(appointments)
            appointment_list = []
            for appointment in appointments:
                appointment_info = {
                    'appointment_date_time': appointment.appointment_date_time
                }
                appointment_list.append(appointment_info)
            return jsonify({'appointments': appointment_list})
        else:
            return jsonify({'error': 'Doctor not found'}), 404
    else:
        return jsonify({'error': 'Doctor ID and date are required'}), 400


@app.route('/createAppointment', methods=['GET', 'POST'])
# @login_required
def create_appointment():
    if current_user.is_authenticated:
        date = request.form.get('date')
        doctor_id = request.form.get('doctor_id')
        appt_time = request.form.get('appt')
        appointment_details = request.form.get('appointment_details')

        try:
            appmnt_date_time = datetime.strptime(f"{date} {appt_time}", '%Y-%m-%d %H:%M:%S')
        except:
            return 'No time selected', 403
        print(doctor_id)
        print(appmnt_date_time)

        # Выполнение запроса
        appointment = Appointment.query.filter_by(appointment_date_time=str(appmnt_date_time),
                                                  doctor_id=doctor_id).first()
        print(appointment.patient_id)
        if appointment:
            if not appointment.patient_id:
                if current_user.patient:
                    # Обновляем поля записи
                    appointment.patient_id = current_user.patient.id
                    appointment.appointment_details = appointment_details

                    db.session.commit()

                    return 'Appointment successfully updated!', 200
                else:
                    return 'User not authorized as patient to update this appointment.', 403
            else:
                return 'Time already selected. Try again.', 403
        else:
            return 'Appointment not found.', 404
    else:
        return 'Unauthorized.', 401


@app.route('/updateAppointment/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    if current_user.is_authenticated:
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            if current_user.patient and appointment.patient_id == current_user.patient.id:
                date = request.form.get('date')
                doctor_id = request.form.get('doctor_id')
                appt_time = request.form.get('appt')
                appointment_details = request.form.get('appointment_details')

                appointment_date_time = datetime.strptime(f"{date} {appt_time}", '%Y-%m-%d %H:%M:%S')

                # Обновляем поля записи
                appointment.doctor_id = doctor_id
                appointment.appointment_date_time = appointment_date_time
                appointment.appointment_details = appointment_details

                db.session.commit()

                return jsonify({'message': 'Appointment successfully updated!'}), 200
            else:
                return jsonify({'error': 'User not authorized to update this appointment.'}), 403
        else:
            return jsonify({'error': 'Appointment not found.'}), 404
    else:
        abort(401)  # Unauthorized


@app.route('/menu')
@login_required
def menu():
    template = 'menu.html'

    if current_user.patient:
        return render_template(template)
    else:
        return 'Doctor', 404


@app.route('/appointments')
@login_required
def appointments():
    if current_user.patient:
        user = current_user.patient
        appointments = Appointment.query.filter_by(patient_id=user.id).all()
        return render_template('appointments.html', appointments=appointments)
    else:
        return 'Unauthorized', 403


@app.route('/login', methods=['GET', 'POST'])
def login():
    template = 'login.html'
    form: LoginForm = LoginForm()
    if form.validate_on_submit():
        email = form.username.data
        password = form.password.data
        user: User = User.query.filter_by(username=email).first()
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    return render_template(template, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('signup.html')


@app.route('/signup_doctor', methods=['GET', 'POST'])
def signup_doctor():
    template = 'signupDoctor.html'
    form: DoctorForm = DoctorForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        if user:
            flash('Пользователь с этим адресом электронной почты уже существует.', 'error')
            return render_template(template, form=form)

        filename = save_file(form.photo.data)

        new_user = User(
            form.email.data,
            form.password.data
        )

        new_doctor = Doctor(
            surname=form.surname.data,
            firstname=form.firstname.data,
            patronymic=form.patronymic.data,
            dob=form.dob.data,
            education=form.education.data,
            workplace=form.workplace.data,
            practice_profile=form.practice_profile.data,
            phone=form.phone.data,
            photo_path=filename,
            user=new_user
        )
        db.session.add(new_user)
        db.session.add(new_doctor)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template(template, form=form)


@app.route('/signup_patient', methods=['GET', 'POST'])
def signup_patient():
    template = 'signupPatient.html'
    form: PatientForm = PatientForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        if user:
            flash('Пользователь с этим адресом электронной почты уже существует.', 'error')
            return render_template(template, form=form)

        filename = save_file(form.photo.data)

        new_user = User(
            form.email.data,
            form.password.data
        )

        new_patient = Patient(
            surname=form.surname.data,
            firstname=form.firstname.data,
            dob=form.dob.data,
            region=form.region.data,
            phone=form.phone.data,
            photo_path=filename,
            user=new_user
        )
        db.session.add(new_user)
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template(template, form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
