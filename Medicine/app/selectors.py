from flask_login import current_user
from sqlalchemy import func

from app import db
from app.models import User, Doctor, Appointment, Diagnostic


def select_practice_profiles():
    practice_profiles = Doctor.query.with_entities(Doctor.practice_profile).distinct().all()
    return [profile[0] for profile in practice_profiles]


def select_appointment_by_target_date(target_date):
    return (
        Appointment.query
        .filter_by(doctor_id=current_user.doctor.id)
        .filter(func.date(Appointment.appointment_date_time) == target_date)
        .order_by(Appointment.appointment_date_time)
    )


def select_appointment_by_patient(patient):
    return (
        Appointment.query
        .filter_by(patient_id=patient.id)
        .order_by(Appointment.appointment_date_time)
        .all()
    )


def select_appointment_by_doctor_and_date(doctor: Doctor, date):
    return (
        Appointment.query
        .filter_by(doctor_id=doctor.id)
        .filter(db.func.date(Appointment.appointment_date_time) == date.date())
        .all()
    )


def select_diagnostics_by_user_id(user: User):
    return (
        Diagnostic.query
        .filter_by(user_id=user.id)
        .order_by(Diagnostic.date.desc())
        .all()
    )
