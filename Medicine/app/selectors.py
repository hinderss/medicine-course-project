from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func

from app import disease_definer
from app.decorators import doctor_required, patient_required
from app.exceptions import *
from app.helpers import save_file
from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager, TODAY
from app.forms import LoginForm, DoctorForm, PatientForm, MedicalCardForm, AppointmentForm, DoctorScheduleForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment, Schedule
from app.serializers import doctors_schema
from app.success import HttpSuccess


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

