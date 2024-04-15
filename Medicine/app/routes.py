from datetime import datetime
from app.helpers import save_file
from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from app.forms import LoginForm, DoctorForm, PatientForm, MedicalCardForm, AppointmentForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'
    form: AppointmentForm = AppointmentForm()

    if current_user.is_authenticated:
        if current_user.patient:
            user = current_user.patient
        else:
            user = current_user.doctor
        name = user.firstname
        surname = user.surname
        return render_template(template, name=name, surname=surname, form=form)

    return render_template(template, form=form)


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
            form.populate_obj(existing_med_card)
        else:
            new_med_card = MedicalCard(patient_id=current_user.patient.id)
            form.populate_obj(new_med_card)
            db.session.add(new_med_card)

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


@app.route('/practice_profiles', methods=['GET'])
def get_practice_profiles():
    practice_profiles = Doctor.query.with_entities(Doctor.practice_profile).distinct().all()
    practice_profiles = [profile[0] for profile in practice_profiles]

    return jsonify({'practice_profiles': practice_profiles})


@app.route('/appointments/get_doctor_time')
def get_doctor_appointments():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')
    if doctor_id and date_str:
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            appointments = Appointment.query.filter_by(doctor_id=doctor_id) \
                .filter(db.func.date(Appointment.appointment_date_time) == date.date()) \
                .filter(Appointment.patient_id.is_(None)) \
                .all()
            appointments_dict = [
                {'appointment_date_time': appointment.appointment_date_time}
                for appointment in appointments
            ]
            return jsonify({'appointments': appointments_dict})
        else:
            return jsonify({'error': 'Doctor not found'}), 404
    else:
        return jsonify({'error': 'Doctor ID and date are required'}), 400


@app.route('/createAppointment', methods=['GET', 'POST'])
@login_required
def create_appointment():
    form: AppointmentForm = AppointmentForm()
    if form.validate_on_submit():
        date = datetime.strptime(form.date.data, '%Y-%m-%d')
        time = datetime.strptime(form.time.data, '%H:%M:%S').time()
        date_time = datetime.combine(date, time)

        appointment = Appointment.query.filter_by(appointment_date_time=str(date_time),
                                                  doctor_id=form.doctor_id.data).first()
        if appointment:
            if not appointment.patient_id:
                if current_user.patient:
                    appointment.patient_id = current_user.patient.id
                    appointment.appointment_details = form.appointment_details.data
                    db.session.commit()
                    return jsonify({'message': 'Appointment successfully updated!'}), 200
                else:
                    return jsonify({'error': 'User not authorized as patient to update this appointment.'}), 403
            else:
                return jsonify({'error': 'Time already selected. Try again.'}), 403
        else:
            return jsonify({'error': 'Appointment not found.'}), 404
    else:
        errors = {field: error for field, error in form.errors.items()}
        return jsonify(errors), 400


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
    template = 'appointments.html'
    if current_user.patient:
        user = current_user.patient
        appointments = Appointment.query.filter_by(patient_id=user.id).all()
        return render_template(template, appointments=appointments)
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
