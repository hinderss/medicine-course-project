from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func

from app import disease_definer, PER_PAGE, WEEKDAYS
from app.decorators import doctor_required, patient_required, transaction_atomic
from app.exceptions import *
from app.helpers import save_file
from flask import render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager, TODAY
from app.forms import LoginForm, DoctorForm, PatientForm, MedicalCardForm, AppointmentForm, DoctorScheduleForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment, Schedule
from app.serializers import doctors_schema
from app.shortcuts import render_form_template, get_object_or_404, render_form_flash_template, create_model_instance, update_model_instance, delete_model_instance
from app.success import HttpSuccess
import app.selectors as selectors


def filter_doctors(query, *, specialty, experience, price, rating):
    if specialty:
        query = query.filter(Doctor.practice_profile == specialty)

    if experience:
        query = query.filter(Doctor.experience_years >= experience)

    if price:
        price_filters = {
            'below30': Doctor.consultation_price < 30,
            '30_50': Doctor.consultation_price.between(30, 50),
            '50_80': Doctor.consultation_price.between(50, 80),
            'above100': Doctor.consultation_price >= 100,
        }

        filter_condition = price_filters.get(price, True)
        query = query.filter(filter_condition)

    if rating:
        min_rating = int(rating[0])
        query = query.filter(Doctor.rating == min_rating)

    sort_by = request.args.get('sort_by', 'rating')
    order = request.args.get('order', 'desc')
    sort_field = getattr(Doctor, sort_by, None)

    if sort_field:
        query = query.order_by(sort_field.asc() if order == 'asc' else sort_field.desc())

    return query


def get_appointments():
    appointments_by_day = {}
    appointments_times = {}
    days = {}

    for i in range(0, 5):
        target_date = TODAY + timedelta(days=i)
        appointments_by_day[f'day{i}'] = selectors.select_appointment_by_target_date(target_date)
        appointments_times[f'day{i}'] = [
            appointment.appointment_date_time.strftime('%H:%M') for appointment in appointments_by_day[f'day{i}']
        ]
        days[f'day{i}'] = target_date.strftime('%d.%m.%Y')

    return appointments_by_day, appointments_times, days


def get_weekly_schedule():
    weekly_schedule = {}

    for index, day in enumerate(WEEKDAYS):
        schedule = Schedule.query.filter_by(doctor_id=current_user.doctor.id, weekday=index).first()
        weekly_schedule[day] = schedule

    return weekly_schedule
