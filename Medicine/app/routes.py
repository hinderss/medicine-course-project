import os
from datetime import datetime

from sqlalchemy import cast, Date
from werkzeug.utils import secure_filename

from app.validator import Validator
from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify, abort
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
# from app.forms import LoginForm, RegistrationForm, DoctorRegistrationForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'
    name = ''
    surname = ''
    patient = ''

    if current_user.is_authenticated:
        if current_user.patient:
            user = current_user.patient
            patient = 'True'
        elif current_user.doctor:
            user = current_user.doctor
        else:
            return render_template(template)

        name = user.firstname
        surname = user.surname

    return render_template(template, name=name, surname=surname, patient=patient)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/medical_card', methods=['GET', 'POST'])
@login_required
def medical_card():
    template = 'medicalCard.html'
    error = None
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not current_user.patient:  # Check if the logged-in user is a patient
        return "You are not authorized to access this page. Enter as patient"

    patient = current_user.patient
    existing_med_card = MedicalCard.query.filter_by(patient_id=patient.id).first()
    if existing_med_card:
        form_data = {
            'surname': existing_med_card.surname,
            'firstname': existing_med_card.firstname,
            'patronymic': existing_med_card.patronymic,
            'gender': existing_med_card.gender,
            'dob': existing_med_card.dob.strftime("%d.%m.%Y"),
            'passport': existing_med_card.passport,
            'family': existing_med_card.family,
            'document_type': existing_med_card.document_type,
            'document_serial': existing_med_card.document_serial,
            'document_number': existing_med_card.document_number,
            'document_authority': existing_med_card.document_authority,
            'document_issue_date': existing_med_card.document_issue_date.strftime("%d.%m.%Y"),
            'region': existing_med_card.region,
            'city': existing_med_card.city,
            'street': existing_med_card.street,
            'house': existing_med_card.house,
            'building': existing_med_card.building,
            'entrance': existing_med_card.entrance,
            'apartment': existing_med_card.apartment,
            'home_phone': existing_med_card.home_phone,
            'registration_region': existing_med_card.registration_region,
            'registration_city': existing_med_card.registration_city,
            'registration_street': existing_med_card.registration_street,
            'registration_house': existing_med_card.registration_house,
            'registration_building': existing_med_card.registration_building,
            'registration_entrance': existing_med_card.registration_entrance,
            'registration_apartment': existing_med_card.registration_apartment,
            'insurance_serial': existing_med_card.insurance_serial,
            'insurance_number': existing_med_card.insurance_number,
            'disability': existing_med_card.disability,
            'disability_group': existing_med_card.disability_group,
            'benefit_document': existing_med_card.benefit_document,
            'payment_type': existing_med_card.payment_type,
            'allergic_history': existing_med_card.allergic_history,
            'medication_intolerance': existing_med_card.medication_intolerance,
            'blood_group': existing_med_card.blood_group,
            'rhesus': existing_med_card.rhesus,
            'blood_belongs': existing_med_card.blood_belongs,
            'vaccine_reactions': existing_med_card.vaccine_reactions,
            'blood_transfusion': existing_med_card.blood_transfusion,
            'surgical_intervention': existing_med_card.surgical_intervention,
            'previous_infectious_diseases': existing_med_card.previous_infectious_diseases
        }
    else:
        form_data = {
            'surname': patient.surname,
            'firstname': patient.firstname,
            'dob': patient.dob.strftime("%d.%m.%Y")
        }

    if request.method == 'POST':
        surname = request.form.get('surname')
        firstname = request.form.get('firstname')
        dob_str = request.form.get('dob')
        document_issue_date_str = request.form.get('document_issue_date')
        region = request.form.get('region')
        print(request.form.get('registration_region'))

        form_data = {
            'surname': request.form.get('surname'),
            'firstname': request.form.get('firstname'),
            'patronymic': request.form.get('patronymic'),
            'gender': request.form.get('gender'),
            'dob': request.form.get('dob'),
            'passport': request.form.get('passport'),
            'family': request.form.get('family'),
            'document_type': request.form.get('document_type'),
            'document_serial': request.form.get('document_serial'),
            'document_number': request.form.get('document_number'),
            'document_authority': request.form.get('document_authority'),
            'document_issue_date': request.form.get('document_issue_date'),
            'region': request.form.get('region'),
            'city': request.form.get('city'),
            'street': request.form.get('street'),
            'house': request.form.get('house'),
            'building': request.form.get('building'),
            'entrance': request.form.get('entrance'),
            'apartment': request.form.get('apartment'),
            'home_phone': request.form.get('home_phone'),
            'registration_region': request.form.get('registration_region'),
            'registration_city': request.form.get('registration_city'),
            'registration_street': request.form.get('registration_street'),
            'registration_house': request.form.get('registration_house'),
            'registration_building': request.form.get('registration_building'),
            'registration_entrance': request.form.get('registration_entrance'),
            'registration_apartment': request.form.get('registration_apartment'),
            'insurance_serial': request.form.get('insurance_serial'),
            'insurance_number': request.form.get('insurance_number'),
            'disability': request.form.get('disability'),
            'disability_group': request.form.get('disability_group'),
            'benefit_document': request.form.get('benefit_document'),
            'payment_type': request.form.get('payment_type'),
            'allergic_history': request.form.get('allergic_history'),
            'medication_intolerance': request.form.get('medication_intolerance'),
            'blood_group': request.form.get('blood_group'),
            'rhesus': request.form.get('rhesus'),
            'blood_belongs': request.form.get('blood_belongs'),
            'vaccine_reactions': request.form.get('vaccine_reactions'),
            'blood_transfusion': request.form.get('blood_transfusion'),
            'surgical_intervention': request.form.get('surgical_intervention'),
            'previous_infectious_diseases': request.form.get('previous_infectious_diseases')
        }

        if not all([surname, firstname, dob_str, region]):
            error = 'All fields are required.'
            return render_template(template, patient=patient, error=error, form_data=form_data)

        field_validator = Validator.validate_med_card(**form_data)
        if field_validator:
            error = field_validator
            return render_template(template, patient=patient, error=error, form_data=form_data)

        dob = datetime.strptime(dob_str, '%d.%m.%Y').date()
        document_issue_date = datetime.strptime(document_issue_date_str, '%d.%m.%Y').date()
        form_data['dob'] = dob
        form_data['document_issue_date'] = document_issue_date

        new_med_card = MedicalCard(**form_data, patient_id=patient.id)
        if existing_med_card:
            db.session.delete(existing_med_card)
        db.session.add(new_med_card)
        current_user.patient.surname = form_data['surname']
        current_user.patient.firstname = form_data['firstname']
        current_user.patient.dob = form_data['dob']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template(template, patient=patient, error=error, form_data=form_data)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/doctors', methods=['GET'])
def get_doctors_by_specialty():
    specialty = request.args.get('specialty')

    if not specialty:
        return jsonify({'error': 'Специальность не указана'}), 400

    # Получаем список врачей по выбранной специальности
    doctors = Doctor.query.filter_by(practice_profile=specialty).all()

    # Преобразуем объекты Doctor в словари для сериализации в JSON
    doctors_list = []
    for doctor in doctors:
        doctor_dict = {
            'id': doctor.id,
            'surname': doctor.surname,
            'firstname': doctor.firstname,
            'patronymic': doctor.patronymic,
            'dob': doctor.dob.isoformat() if doctor.dob else None,
            'education': doctor.education,
            'workplace': doctor.workplace,
            'phone': doctor.phone,
            'photo_path': doctor.photo_path
        }
        doctors_list.append(doctor_dict)

    return jsonify(doctors_list)


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
        # if current_user.patient is not None:
        #     date = request.form.get('date')
        #     doctor_id = request.form.get('doctor_id')
        #     patient_id = current_user.patient.id
        #     appt_time = request.form.get('appt')
        #     appointment_details = request.form.get('appointment_details')
        #
        #     appointment_date_time = datetime.strptime(f"{date} {appt_time}", '%Y-%m-%d %H:%M:%S')
        #
        #     appointment = Appointment(
        #         doctor_id=doctor_id,
        #         patient_id=patient_id,
        #         appointment_date_time=appointment_date_time,
        #         appointment_details=appointment_details
        #     )
        #
        #     db.session.add(appointment)
        #     db.session.commit()
        #
        #     return jsonify({'message': 'Appointment successfully scheduled!'}), 200
        # elif current_user.doctor is not None:
        #     return jsonify({'error': 'Doctors cannot create appointments.'}), 403
        # else:
        #     return jsonify({'error': 'User not authorized to create appointments.'}), 40


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
        user = current_user.patient
        patient = 'True'
    else:
        return 'Doctor', 404

    name = user.firstname
    surname = user.surname
    email = current_user.username
    return render_template(template, patient=user, name=name, surname=surname, email=email)


@app.route('/appointments')
@login_required
def appointments():
    if current_user.patient:
        user = current_user.patient
        appointments = Appointment.query.filter_by(patient_id=user.id).all()
        return render_template('appointments.html', appointments=appointments)
    else:
        return 'Unauthorized', 403
# @app.route('/appointments/<int:doctor_id>')
# def get_doctor_appointments(doctor_id):
#     doctor = Doctor.query.get(doctor_id)
#     if doctor:
#         appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
#         appointment_list = []
#         for appointment in appointments:
#             appointment_info = {
#                 'id': appointment.id,
#                 'appointment_date_time': appointment.appointment_date_time,
#                 'appointment_details': appointment.appointment_details,
#                 'patient': {
#                     'id': appointment.patient.id,
#                     'surname': appointment.patient.surname,
#                     'firstname': appointment.patient.firstname,
#                     'dob': appointment.patient.dob,
#                     'region': appointment.patient.region,
#                     'phone': appointment.patient.phone,
#                     'photo_path': appointment.patient.photo_path
#                 }
#             }
#             appointment_list.append(appointment_info)
#         return jsonify({'doctor': str(doctor), 'appointments': appointment_list})
#     else:
#         return jsonify({'error': 'Doctor not found'}), 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        if True:    # validate
            user = User.query.filter_by(username=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('signup.html')
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     existing_user = User.query.filter_by(username=form.username.data).first()
    #     if existing_user:
    #         flash('Username is already taken. Please choose a different one.', 'danger')
    #     else:
    #         hashed_password = generate_password_hash(form.password.data)
    #         new_user = User(username=form.username.data, password=hashed_password)
    #         db.session.add(new_user)
    #         db.session.commit()
    #         flash('Registration successful! You can now log in.', 'success')
    #         return redirect(url_for('login'))
    # return render_template('signup.html', form=form)


@app.route('/signup_doctor', methods=['GET', 'POST'])
def signup_doctor():
    template = 'signupDoctor.html'
    error = None
    form_data = {}

    if request.method == 'POST':
        surname = request.form.get('surname')
        firstname = request.form.get('firstname')
        patronymic = request.form.get('patronymic')
        dob_str = request.form.get('dob')
        education = request.form.get('education')
        workplace = request.form.get('workplace')
        practice_profile = request.form.get('practice_profile')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        form_data = {
            'surname': surname,
            'firstname': firstname,
            'patronymic': patronymic,
            'dob': dob_str,
            'education': education,
            'workplace': workplace,
            'practice_profile': practice_profile,
            'phone': phone,
            'email': email
        }

        # Проверка на пустые поля
        if not all([surname, firstname, patronymic, dob_str, education, workplace, practice_profile, phone, email,
                    password]):
            error = 'All fields are required.'
            return render_template(template, error=error, form_data=form_data)

        field_validator = Validator.validate_doctor(**form_data, password=password)
        if field_validator:
            error = field_validator
            return render_template(template, error=error, form_data=form_data)

        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            error = 'User with this email already exists.'
            return render_template(template, error=error, form_data=form_data)

        if 'photo' not in request.files:
            error = 'No photo provided.'
            return render_template(template, error=error, form_data=form_data)

        photo = request.files['photo']
        if photo.filename == '':
            error = 'No selected photo.'
            return render_template(template, error=error, form_data=form_data)

        if not Validator.allowed_file(photo.filename):
            error = 'Invalid photo file type.'
            return render_template(template, error=error, form_data=form_data)

        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        dob = datetime.strptime(dob_str, '%d.%m.%Y').date()
        form_data['dob'] = dob
        form_data.pop('email')
        new_user = User(email, password)

        new_doctor = Doctor(**form_data, doctor=new_user, photo_path=filename)
        db.session.add(new_user)
        db.session.add(new_doctor)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template(template, error=error, form_data=form_data)


@app.route('/signup_patient', methods=['GET', 'POST'])
def signup_patient():
    template = 'signupPatient.html'
    error = None
    form_data = {}

    if request.method == 'POST':
        surname = request.form.get('surname')
        firstname = request.form.get('firstname')
        dob_str = request.form.get('dob')
        region = request.form.get('region')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        form_data = {
            'surname': surname,
            'firstname': firstname,
            'dob': dob_str,
            'region': region,
            'phone': phone,
            'email': email
        }

        # Проверка на пустые поля
        if not all([surname, firstname, dob_str, region, phone, email, password]):
            error = 'All fields are required.'
            return render_template(template, error=error, form_data=form_data)

        field_validator = Validator.validate_patient(**form_data, password=password)
        if field_validator:
            error = field_validator
            return render_template(template, error=error, form_data=form_data)

        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            error = 'User with this email already exists.'
            return render_template(template, error=error, form_data=form_data)

        if 'photo' not in request.files:
            error = 'No photo provided.'
            return render_template(template, error=error, form_data=form_data)

        photo = request.files['photo']
        if photo.filename == '':
            error = 'No selected photo.'
            return render_template(template, error=error, form_data=form_data)

        if not Validator.allowed_file(photo.filename):
            error = 'Invalid photo file type.'
            return render_template(template, error=error, form_data=form_data)

        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        new_user = User(email, password)

        dob = datetime.strptime(dob_str, '%d.%m.%Y').date()
        form_data['dob'] = dob
        form_data.pop('email')

        new_patient = Patient(**form_data, user=new_user, photo_path=filename)
        db.session.add(new_user)
        db.session.add(new_patient)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template(template, error=error, form_data=form_data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
