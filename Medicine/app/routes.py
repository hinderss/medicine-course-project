from datetime import datetime, timedelta

from sqlalchemy import func

from app import disease_definer, PER_PAGE, MAX_DURATION, WEEKDAYS
from app.decorators import doctor_required, patient_required, transaction_atomic
from app.exceptions import *
from app.helpers import save_file
from flask import redirect, url_for, request, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from app import app, login_manager
from app.forms import LoginForm, DoctorForm, PatientForm, MedicalCardForm, AppointmentForm, DoctorScheduleForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment, Schedule
from app.serializers import doctors_schema
from app import services
from app.shortcuts import *
from app.success import HttpSuccess
from app import selectors


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'
    form: AppointmentForm = AppointmentForm()
    symptoms = disease_definer.get_unique_symptoms()
    random_doctors = Doctor.query.order_by(func.random()).limit(10).all()

    if not current_user.is_authenticated:
        return render_template(template, form=form, symptoms=symptoms, doctors_slider=random_doctors)

    if current_user.patient:
        user = current_user.patient
    else:
        user = current_user.doctor
    return render_template(
        template,
        name=user.firstname,
        surname=user.surname,
        form=form,
        symptoms=symptoms,
        doctors_slider=random_doctors,
    )


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/navigation')
def navigate():
    return render_template('navigation.html')

@app.route('/blood_test')
def blood_test():
    return render_template('bloodTest.html')


@app.route('/doctor_appointments')
@login_required
@doctor_required
def doctor_appointments():
    template = 'doctorAppointments.html'
    form: DoctorScheduleForm = DoctorScheduleForm()

    appointments_by_day, appointments_times, days = services.get_appointments()

    return render_template(
        template,
        form=form,
        appointments_by_day=appointments_by_day,
        appointments_times=appointments_times,
        days=days,
        **services.get_weekly_schedule(),
    )


@app.route('/patient-appointments')
@patient_required
def get_patient_appointments():
    template = 'patientAppointments.html'
    patient_appointments = selectors.select_appointment_by_patient(current_user.patient)
    return render_template(template, patient_appointments=patient_appointments)


@app.route('/doctor_list', methods=['GET', 'POST'])
def doctor_list():
    template = 'doctorListPage.html'
    page = request.args.get('page', 1, type=int)

    specialty = request.args.get('specialty')
    experience = request.args.get('experience', type=int)
    price = request.args.get('price')
    rating = request.args.get('rating')

    query = services.filter_doctors(
        Doctor.query,
        specialty=specialty,
        experience=experience,
        price=price,
        rating=rating,
    )

    paginated_doctors = query.paginate(page=page, per_page=PER_PAGE)

    return render_template(
        template,
        doctors=paginated_doctors,
        count=Doctor.query.count(),
        practice_profiles=selectors.select_practice_profiles(),
    )


@app.route('/medical-card', methods=['GET', 'POST'])
@login_required
@patient_required
@transaction_atomic
def medical_card():
    template = 'medicalCard.html'
    form: MedicalCardForm

    patient = current_user.patient

    medical_card = MedicalCard.query.filter_by(patient_id=patient.id).first()

    if medical_card:
        form = MedicalCardForm(obj=medical_card)
        form.populate_obj(medical_card)
    else:
        form = MedicalCardForm(
            surname=patient.surname,
            firstname=patient.firstname,
            dob=patient.dob,
        )
        new_med_card = MedicalCard(patient_id=current_user.patient.id)
        form.populate_obj(new_med_card)
        db.session.add(new_med_card)

    if not form.validate_on_submit():
        return render_form_template(form, template)

    update_model_instance(
        patient,
        commit=False,
        surname=form.surname.data,
        firstname=form.firstname.data,
        dob=form.dob.data,
    )

    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/doctors-by-specialty', methods=['GET'])
def get_doctors_by_specialty():
    specialty = request.args.get('specialty')

    if not specialty:
        raise HttpJson400('Specialty not specified')

    doctors = Doctor.query.filter_by(practice_profile=specialty).all()

    return doctors_schema.jsonify(doctors)


@app.route('/practice-profiles', methods=['GET'])
def get_practice_profiles():
    practice_profiles = Doctor.query.with_entities(Doctor.practice_profile).distinct().all()
    practice_profiles = [profile[0] for profile in practice_profiles]

    return jsonify(practice_profiles)


@app.route('/appointments/available-doctor-time')
def get_available_doctor_time():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')

    if not doctor_id or not date_str:
        raise HttpJson400("Doctor ID and date are required")

    doctor = get_object_or_404(Doctor, error_message="Doctor not found", id=doctor_id)

    date = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = date.weekday()

    schedule = Schedule.query.filter_by(doctor_id=doctor.id, weekday=weekday).first()
    if not schedule:
        return jsonify([])

    assigned = selectors.select_appointment_by_doctor_and_date(doctor=doctor, date=date)
    assigned_times = [assign.appointment_date_time for assign in assigned]

    start_time = datetime.combine(date, schedule.start_time)
    end_time = datetime.combine(date, schedule.end_time)
    step = timedelta(minutes=schedule.duration_minutes)

    appointments = []
    current_time = start_time
    while current_time <= end_time:
        appointments.append(current_time)
        current_time += step

    appointments = sorted(list(set(appointments) - set(assigned_times)))

    return jsonify(appointments)


@app.route('/assign-appointment', methods=['GET', 'POST'])
def assign_appointment():
    form: AppointmentForm = AppointmentForm()

    if not current_user.is_authenticated:
        raise HttpJson403('Sign in as user to continue.')

    if not form.validate_on_submit():
        return render_form_template(form)

    date = datetime.strptime(form.date.data, '%Y-%m-%d')
    time = datetime.strptime(form.time.data, '%H:%M:%S').time()

    date_time = datetime.combine(date, time).replace(microsecond=0)
    appointment = Appointment.query.filter_by(
        appointment_date_time=date_time,
        doctor_id=form.doctor_id.data,
    ).first()
    if appointment:
        raise HttpJson409('Appointment already created!')
    if not current_user.patient:
        raise HttpJson403('User not authorized as patient to update this appointment.')
    create_model_instance(
        Appointment,
        doctor_id=form.doctor_id.data,
        patient_id=current_user.patient.id,
        appointment_date_time=date_time,
        appointment_details=form.appointment_details.data,
    )
    return HttpSuccess('Appointment successfully created!')


@app.route('/menu')
@login_required
def menu():
    template = 'menu.html'
    return render_template(template)


@app.route('/appointments')
@login_required
@patient_required
def appointments():
    template = 'appointments.html'
    user = current_user.patient
    appoint = Appointment.query.filter_by(patient_id=user.id).all()
    return render_template(template, appointments=appoint)


@app.route('/cancel-appointment', methods=['PUT'])
@login_required
@patient_required
def cancel_appointment():
    appointment_id = request.form.get('appointment_id')
    appointment = get_object_or_404(
        Appointment,
        error_message="Appointment not found",
        id=appointment_id,
    )

    if appointment.patient != current_user.patient:
        raise HttpJson403('You are not allowed to delete this appointment.')

    update_model_instance(appointment, patient_id=None, appointment_details=None)
    return HttpSuccess('Appointment successfully canceled!')


@app.route('/create-appointment', methods=['POST'])
@login_required
@doctor_required
@transaction_atomic
def create_appointment():
    form: DoctorScheduleForm = DoctorScheduleForm()
    doctor_id = current_user.doctor.id
    for i, day in enumerate(WEEKDAYS):
        existing_schedule = Schedule.query.filter_by(doctor_id=doctor_id, weekday=i).first()
        if not getattr(form, f"{day}_check").data:
            if existing_schedule:
                delete_model_instance(existing_schedule, commit=False)
        else:
            try:
                start_time = datetime.strptime(request.form[f'{day}_start_time'], '%H:%M:%S').time()
            except ValueError:
                start_time = datetime.strptime(request.form[f'{day}_start_time'], '%H:%M').time()
            try:
                end_time = datetime.strptime(request.form[f'{day}_end_time'], '%H:%M:%S').time()
            except ValueError:
                end_time = datetime.strptime(request.form[f'{day}_end_time'], '%H:%M').time()

            duration = int(request.form[f'{day}_duration'])
            if duration > MAX_DURATION:
                raise HttpJson400('Too long appointment.')

            schedule_data = {
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration,
            }
            if existing_schedule:
                update_model_instance(
                    existing_schedule,
                    commit=False,
                    **schedule_data,
                )
            else:
                create_model_instance(
                    Schedule,
                    commit=False,
                    doctor_id=doctor_id,
                    weekday=i,
                    **schedule_data,
                )
    return HttpSuccess('Appointment successfully created!')


@app.route('/delete-appointment', methods=['DELETE'])
@login_required
@doctor_required
def delete_appointment():
    appointment_id = request.form.get('appointment_id')
    appointment = get_object_or_404(
        Appointment,
        error_message="Appointment not found",
        id=appointment_id,
    )

    if appointment.doctor != current_user.doctor:
        raise HttpJson403('You are not allowed to delete this appointment.')

    delete_model_instance(appointment)
    return HttpSuccess('Appointment successfully deleted!')


@app.route('/login', methods=['GET', 'POST'])
def login():
    template = 'login.html'
    form: LoginForm = LoginForm()
    if not form.validate_on_submit():
        return render_form_template(form, template)

    email = form.username.data
    password = form.password.data
    user = User.query.filter_by(username=email).first()

    if (not user) or (not user.verify_password(password)):
        return render_form_flash_template(form, template, message='Invalid username or password. Please try again.')

    login_user(user)
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('signup.html')


@app.route('/signup-doctor', methods=['GET', 'POST'])
@transaction_atomic
def signup_doctor():
    template = 'signupDoctor.html'
    form: DoctorForm = DoctorForm()
    if not form.validate_on_submit():
        return render_form_template(form, template)

    user = User.query.filter_by(username=form.email.data).first()
    if user:
        return render_form_flash_template(form, template, message='User with this email address already exists.')

    filename = save_file(form.photo.data)

    new_user = create_model_instance(
        user,
        commit=False,
        email=form.email.data,
        password=form.password.data,
    )

    create_model_instance(
        Doctor,
        commit=False,
        surname=form.surname.data,
        firstname=form.firstname.data,
        patronymic=form.patronymic.data,
        dob=form.dob.data,
        education=form.education.data,
        workplace=form.workplace.data,
        practice_profile=form.practice_profile.data,
        phone=form.phone.data,
        photo_path=filename,
        user=new_user,
    )
    return redirect(url_for('login'))


@app.route('/signup-patient', methods=['GET', 'POST'])
@transaction_atomic
def signup_patient():
    template = 'signupPatient.html'
    form: PatientForm = PatientForm()

    if not form.validate_on_submit():
        return render_form_template(form, template)
    user = User.query.filter_by(username=form.email.data).first()
    if user:
        return render_form_flash_template(form, template, message='User with this email address already exists.')

    filename = save_file(form.photo.data)

    new_user = create_model_instance(
        user,
        commit=False,
        email=form.email.data,
        password=form.password.data,
    )

    create_model_instance(
        Patient,
        commit=False,
        surname=form.surname.data,
        firstname=form.firstname.data,
        dob=form.dob.data,
        region=form.region.data,
        phone=form.phone.data,
        photo_path=filename,
        user=new_user
    )
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return User.query.get(user_id)


@app.route('/diagnose', methods=['POST'])
def diagnose():
    symptoms = request.json.get('symptoms', [])
    possible_diseases = disease_definer.get_possible_disease(symptoms)

    return jsonify(possible_diseases)
