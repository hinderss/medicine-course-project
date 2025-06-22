import os
from datetime import datetime, timedelta

from langchain_community.chat_models import ChatOpenAI
from sqlalchemy import func

from app import disease_definer, PER_PAGE, MAX_DURATION, WEEKDAYS, ag, diseases_json, endocrine_system_json, \
    vitamin_system_json, micronutrients_data, symptoms_json
from app.decorators import doctor_required, patient_required, transaction_atomic
from app.exceptions import *
from app.helpers import save_file
from flask import redirect, url_for, request, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from app import app, login_manager
from app.forms import LoginForm, DoctorForm, PatientForm, MedicalCardForm, AppointmentForm, DoctorScheduleForm, \
    NavigationForm, RecommendationForm, CommonBloodForm, MicronutrientsBloodForm, VitaminBloodForm, HormonesBloodForm
from app.models import User, Doctor, Patient, MedicalCard, Appointment, Schedule, Diagnostic, ChatMessage
from app.serializers import doctors_schema, LoginSerializer, RegisterSerializer, ApiSerializer, BloodSerializer, \
    BloodListOfDictsSerializer
from app import services
from app.shortcuts import *
from app.success import HttpSuccess
from app import selectors

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# llm = Ollama(
#     model="gemma3:4b",
#     temperature=0.7,
#     top_p=0.9,
#     num_ctx=2048,
# )

llm = ChatOpenAI(
    base_url=os.getenv('GPT_URL'),
    api_key=os.getenv('GPT_API_KEY'),
    model="gemini-2.0-flash-lite",
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Ты - полезный AI-ассистент DeepSeek-R1. Отвечай вежливо и информативно. Отвечай строго на русском языке"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    endpoint = data.get('endpoint', '').strip()

    if not user_message:
        return jsonify({'response': 'Сообщение не может быть пустым'}), 400

    try:
        context = get_medical_context(current_user, endpoint)

        user_msg = ChatMessage(
            user_id=current_user.id,
            message=user_message,
            is_user=True,
        )
        db.session.add(user_msg)
        db.session.commit()

        history = ChatMessage.query.filter_by(user_id=current_user.id) \
            .order_by(ChatMessage.timestamp.desc()).limit(10).all()
        history = list(reversed(history))

        lc_history = []
        for msg in history:
            if msg.is_user:
                lc_history.append(HumanMessage(content=msg.message))
            else:
                lc_history.append(AIMessage(content=msg.message))

        system_message = f"""
        Ты - медицинский AI-ассистент. Отвечай профессионально и точно. Старайся выдавать короткие ответы.
        Текущая страница: {endpoint}. 
        Контекст пользователя:
        {context}
        """

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])

        chain = prompt_template | llm
        response_message = chain.invoke({
            "input": user_message,
            "history": lc_history
        })
        response = response_message.content.strip()

        response = response.replace("AI: ", "")

        bot_msg = ChatMessage(
            user_id=current_user.id,
            message=response,
            is_user=False
        )
        db.session.add(bot_msg)
        db.session.commit()

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f'Ошибка: {str(e)}'}), 500


def get_medical_context(user, endpoint):
    """Возвращает детализированный медицинский контекст с учетом всех полей карты"""
    context_parts = []

    # Базовый контекст пользователя
    if user.patient:
        patient = user.patient
        context_parts.append(f"Собеседник: Пациент: {patient.firstname} {patient.surname}")
        context_parts.append(f"- Дата рождения: {patient.dob.strftime('%d.%m.%Y') if patient.dob else 'не указана'}")
        context_parts.append(f"- Контактный телефон: {patient.phone or 'не указан'}")
    elif user.doctor:
        doctor = user.doctor
        context_parts.append(f"Собеседник: Врач: {doctor.firstname} {doctor.surname}")
        context_parts.append(f"- Специализация: {doctor.practice_profile or 'не указана'}")

    # Детализированный контекст медицинской карты
    if user.patient:
        medical_card = MedicalCard.query.filter_by(patient_id=user.patient.id).first()
        if medical_card:
            context_parts.append("\n## Медицинская карта:")

            # Персональные данные
            personal_info = [
                f"- Пол: {medical_card.gender}" if medical_card.gender else None,
                f"- Паспорт: {medical_card.passport}" if medical_card.passport else None,
                f"- Семейное положение: {medical_card.family}" if medical_card.family else None
            ]
            context_parts.extend(filter(None, personal_info))

            # Документы
            if medical_card.document_type:
                doc_info = f"- Документ: {medical_card.document_type} {medical_card.document_serial} №{medical_card.document_number}"
                if medical_card.document_authority:
                    doc_info += f", выдан {medical_card.document_authority}"
                if medical_card.document_issue_date:
                    doc_info += f" {medical_card.document_issue_date.strftime('%d.%m.%Y')}"
                context_parts.append(doc_info)

            # Адреса
            address_info = [
                f"- Адрес проживания: {format_address(medical_card)}" if has_address_data(medical_card) else None,
                f"- Адрес регистрации: {format_registration_address(medical_card)}" if has_registration_data(
                    medical_card) else None
            ]
            context_parts.extend(filter(None, address_info))

            # Страховые данные
            if medical_card.insurance_serial or medical_card.insurance_number:
                context_parts.append(
                    f"- Страховой полис: {medical_card.insurance_serial or ''} №{medical_card.insurance_number or ''}")

            # Медицинские данные
            medical_info = [
                f"- Группа крови: {medical_card.blood_group} {medical_card.rhesus}" if medical_card.blood_group else None,
                f"- Инвалидность: {medical_card.disability}, группа {medical_card.disability_group}" if medical_card.disability else None,
                f"- Льготы: {medical_card.benefit_document}" if medical_card.benefit_document else None,
                f"- Тип оплаты: {medical_card.payment_type}" if medical_card.payment_type else None
            ]
            context_parts.extend(filter(None, medical_info))

            # Медицинская история
            medical_history = [
                f"\n### Аллергологический анамнез:\n{medical_card.allergic_history}" if medical_card.allergic_history else None,
                f"\n### Непереносимость лекарств:\n{medical_card.medication_intolerance}" if medical_card.medication_intolerance else None,
                f"\n### Перенесенные операции:\n{medical_card.surgical_intervention}" if medical_card.surgical_intervention else None,
                f"\n### Инфекционные заболевания:\n{medical_card.previous_infectious_diseases}" if medical_card.previous_infectious_diseases else None,
                f"\n### Реакции на вакцины:\n{medical_card.vaccine_reactions}" if medical_card.vaccine_reactions else None,
                f"\n### Переливания крови:\n{medical_card.blood_transfusion}" if medical_card.blood_transfusion else None
            ]
            context_parts.extend(filter(None, medical_history))

    # Контекст диагностик (последние 3)
    diagnostics = Diagnostic.query.filter_by(user_id=user.id) \
        .order_by(Diagnostic.date.desc()).limit(3).all()
    if diagnostics:
        context_parts.append("\n## Последние диагностики:")
        for d in diagnostics:
            result_summary = ", ".join([f"{k}: {v[:50]}..." if len(str(v)) > 50 else f"{k}: {v}"
                                        for k, v in d.result.items()])
            selected_summary = ", ".join([f"{k}: {v[:50]}..." if len(str(v)) > 50 else f"{k}: {v}"
                                        for k, v in d.selected.items()])
            context_parts.append(f"- {d.type} ({d.date.strftime('%d.%m.%Y')}): {selected_summary}: {result_summary}")

    # Контекст записей к врачу (ближайшие 3)
    if user.patient:
        now = datetime.now()
        appointments = Appointment.query.filter(
            Appointment.patient_id == user.patient.id,
            Appointment.appointment_date_time >= now
        ).order_by(Appointment.appointment_date_time.asc()).limit(3).all()

        if appointments:
            context_parts.append("\n## Ближайшие записи:")
            for a in appointments:
                context_parts.append(
                    f"- {a.appointment_date_time.strftime('%d.%m.%Y %H:%M')}: "
                    f"прием у {a.doctor.surname} {a.doctor.firstname} "
                    f"({a.doctor.practice_profile})"
                )

    # Специфический контекст страницы
    page_context = get_page_specific_context(endpoint)
    context_parts.append(f"\n## Контекст страницы:\n{page_context}")

    return "\n".join(context_parts)


def format_address(card):
    """Форматирует адрес проживания"""
    parts = [
        card.region,
        card.city,
        card.street,
        f"д. {card.house}" if card.house else None,
        f"корп. {card.building}" if card.building else None,
        f"под. {card.entrance}" if card.entrance else None,
        f"кв. {card.apartment}" if card.apartment else None
    ]
    return ", ".join(filter(None, parts))


def format_registration_address(card):
    """Форматирует адрес регистрации"""
    parts = [
        card.registration_region,
        card.registration_city,
        card.registration_street,
        f"д. {card.registration_house}" if card.registration_house else None,
        f"корп. {card.registration_building}" if card.registration_building else None,
        f"под. {card.registration_entrance}" if card.registration_entrance else None,
        f"кв. {card.registration_apartment}" if card.registration_apartment else None
    ]
    return ", ".join(filter(None, parts))


def has_address_data(card):
    """Проверяет наличие данных об адресе"""
    return any([card.region, card.city, card.street, card.house])


def has_registration_data(card):
    """Проверяет наличие данных о регистрации"""
    return any([card.registration_region, card.registration_city,
                card.registration_street, card.registration_house])


def get_page_specific_context(endpoint):
    """Возвращает контекст для конкретной страницы"""
    contexts = {
        '/medical-card': """
        Вы находитесь на странице медицинской карты. Доступные действия:
        - Редактирование персональных данных
        - Обновление медицинской истории
        - Просмотр и изменение адресов
        - Управление страховыми данными
        """,
        '/diagnostic_history': """
        Страница истории диагностик. Здесь отображаются:
        - Все проведенные исследования и анализы
        - Результаты с интерпретацией
        - Рекомендации по результатам
        - Возможность экспорта данных
        """,
        '/blood_test': """
        Раздел анализов крови. Доступные функции:
        - Ввод результатов анализов
        - Автоматическая интерпретация показателей
        - Сравнение с предыдущими результатами
        - Формирование рекомендаций
        """,
        '/patient-appointments': """
        Раздел записей на прием. Возможные действия:
        - Просмотр предстоящих визитов
        - Отмена или перенос записей
        - Просмотр истории посещений
        - Оценка проведенных приемов
        """
    }
    return contexts.get(endpoint, "Медицинский портал. Выберите нужный раздел для работы.")


@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    if not current_user.is_authenticated:
        return jsonify({'messages': []})

    messages = ChatMessage.query.filter_by(user_id=current_user.id) \
        .order_by(ChatMessage.timestamp.asc()).all()

    return jsonify({
        'messages': [{
            'text': msg.message,
            'is_user': msg.is_user,
            'time': msg.timestamp.strftime('%H:%M')
        } for msg in messages]
    })


@app.route('/chat/clear', methods=['POST'])
def clear_chat_history():
    if not current_user.is_authenticated:
        return jsonify({'response': 'Требуется авторизация'}), 401

    try:
        ChatMessage.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'response': 'История чата очищена'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'response': f'Ошибка при очистке: {str(e)}'}), 500



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


@app.route('/navigation', methods=['GET', 'POST'])
def navigate():
    template = 'navigation.html'
    form: NavigationForm = NavigationForm()
    if not form.validate_on_submit():
        return render_form_template(form, template)

    agent_output = ag.nav(form.query.data, form.language.data)
    if not ag.success():
        return render_form_flash_template(form, template, message='Agent error')
    result = ApiSerializer().load(agent_output)

    if result.get("message") == "Not Found":
        return render_form_flash_template(form, template, message='Agent says: Not Found.')

    # return render_form_template(form, template)
    if current_user.patient:
        user = current_user.patient
    else:
        user = current_user.doctor
    return render_template(
        template,
        name=user.firstname,
        surname=user.surname,
        form=form,
        answer=result.get("message"),
    )


@app.route('/common_blood_test', methods=['GET', 'POST'])
def common_blood_test():

    form: CommonBloodForm = CommonBloodForm()

    if request.method == 'GET' or not form.validate_on_submit():
        return jsonify(form.errors), 400

    agent_output = ag.blood(wbc=form.leukocytes.data, rbc=form.erythrocytes.data, platelets=form.platelets.data)

    if not ag.success():
        return jsonify({
            'status': 'error',
            'message': 'Agent error'
        }), 500

    result = BloodSerializer().load(agent_output)

    if not result.get("message"):
        return jsonify({
            'status': 'success',
            'result': 'Норма',
            'recommendation': 'Все показатели в пределах нормы'
        })

    if result.get("message") == "Not Found":
        return jsonify({
            'status': 'error',
            'message': 'Agent says: Not Found.'
        }), 404

    diagnoses = result.get("message", [])
    answers = [diseases_json.get(disease, {
        'result': 'Неизвестное состояние',
        'recommendation': 'Требуется консультация специалиста'
    }) for disease in diagnoses]

    full_result = ", ".join([answer['result'] for answer in answers])
    full_recommendation = "\n".join([answer['recommendation'] for answer in answers])

    if current_user.is_authenticated:
        create_model_instance(
            Diagnostic,
            type="Общий анализ крови",
            user_id=current_user.id,
            selected={
                "Тромбоциты": form.platelets.data,
                "Эритроциты": form.erythrocytes.data,
                "Лейкоциты": form.leukocytes.data,
            },
            result={answer['result']: answer['recommendation'] for answer in answers},
        )

    return jsonify({
        'status': 'success',
        'result': full_result,
        'recommendation': full_recommendation,
        'diagnoses': diagnoses,
        'detailed_answers': answers
    })


@app.route('/micronutrients_blood_test', methods=['GET', 'POST'])
def micronutrients_blood_test():
    form: MicronutrientsBloodForm = MicronutrientsBloodForm()

    if request.method == 'GET':
        return jsonify({'status': 'error', 'message': 'Use POST method for submission'}), 400

    if not form.validate_on_submit():
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': form.errors
        }), 400

    agent_output = ag.micronutrients_blood(ca=form.calcium.data, mg=form.magnium.data, fe=form.ferrum.data)
    if not ag.success():
        return jsonify({
            'status': 'error',
            'message': 'Medical analysis failed',
            'details': str(agent_output)
        }), 500

    result = BloodListOfDictsSerializer().load(agent_output)
    diagnoses = result.get("message", [])

    answers = []
    for diagnosis in diagnoses:
        vitamin, value = next(iter(diagnosis.items()))
        info = micronutrients_data[vitamin]
        deficiency_excess = info.get(value)
        answers.append({
            "result": f"{'Дефицит' if value == 'deficiency' else 'Избыток'} {info['name']}",
            "recommendation": deficiency_excess["recommendation"]
        })

    full_result = ", ".join([answer['result'] for answer in answers])
    full_recommendation = "\n".join([answer['recommendation'] for answer in answers])

    if current_user.is_authenticated:
        create_model_instance(
            Diagnostic,
            type="Общий анализ крови",
            user_id=current_user.id,
            selected={
                "Кальций": form.calcium.data,
                "Магний": form.magnium.data,
                "Железо": form.ferrum.data,
            },
            result={answer['result']: answer['recommendation'] for answer in answers},
        )

    return jsonify({
        'status': 'success',
        'result': full_result,
        'recommendation': full_recommendation,
        'diagnoses': diagnoses,
        'detailed_answers': answers
    })


@app.route('/vitamin_blood_test', methods=['GET', 'POST'])
def vitamin_blood_test():
    form = VitaminBloodForm()

    # Валидация формы
    if request.method == 'GET':
        return jsonify({'status': 'error', 'message': 'Use POST method for submission'}), 400

    if not form.validate_on_submit():
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': form.errors
        }), 400

    agent_output = ag.vitamin_blood(
        vitamin_e=float(form.vitamin_e.data),
        vitamin_d=float(form.vitamin_d.data),
        vitamin_k=float(form.vitamin_k.data),
        vitamin_c=float(form.vitamin_c.data),
        vitamin_b1=float(form.vitamin_b1.data),
        vitamin_b2=float(form.vitamin_b2.data),
        vitamin_b9=float(form.vitamin_b9.data),
        vitamin_b12=float(form.vitamin_b12.data),
        vitamin_a=float(form.vitamin_a.data),
        vitamin_b6=float(form.vitamin_b6.data)
    )

    if not ag.success():
        return jsonify({
            'status': 'error',
            'message': 'Medical analysis failed',
            'details': str(agent_output)
        }), 500

    result = BloodListOfDictsSerializer().load(agent_output)

    if not result.get("message"):
        return jsonify({
            'status': 'success',
            'result': 'Normal',
            'recommendation': 'All vitamin levels are within normal ranges',
            'vitamin_levels': {
                'vitamin_e': form.vitamin_e.data,
                'vitamin_d': form.vitamin_d.data,
                'vitamin_k': form.vitamin_k.data,
                'vitamin_c': form.vitamin_c.data,
                'vitamin_b1': form.vitamin_b1.data,
                'vitamin_b2': form.vitamin_b2.data,
                'vitamin_b9': form.vitamin_b9.data,
                'vitamin_b12': form.vitamin_b12.data,
                'vitamin_a': form.vitamin_a.data,
                'vitamin_b6': form.vitamin_b6.data
            }
        })

    diagnoses = result.get("message", [])

    answers = []
    for diagnosis in diagnoses:
        vitamin, value = next(iter(diagnosis.items()))
        info = vitamin_system_json[vitamin]
        deficiency_excess = info.get(value)
        answers.append({
            "result": f"{'Дефицит' if value == 'deficiency' else 'Избыток'} {info["name"]}",
            "recommendation": deficiency_excess["recommendation"]
        })

    full_result = ", ".join([answer['result'] for answer in answers])
    full_recommendation = "\n".join([answer['recommendation'] for answer in answers])

    if current_user.is_authenticated:
        create_model_instance(
            Diagnostic,
            type="Анализ на витамины",
            user_id=current_user.id,
            selected={
                'Витамин e': form.vitamin_e.data,
                'Витамин d': form.vitamin_d.data,
                'Витамин k': form.vitamin_k.data,
                'Витамин c': form.vitamin_c.data,
                'Витамин b1': form.vitamin_b1.data,
                'Витамин b2': form.vitamin_b2.data,
                'Витамин b9': form.vitamin_b9.data,
                'Витамин b12': form.vitamin_b12.data,
                'Витамин a': form.vitamin_a.data,
                'Витамин b6': form.vitamin_b6.data
            },
            result={answer['result']: answer['recommendation'] for answer in answers},
        )

    return jsonify({
        'status': 'success',
        'result': full_result,
        'recommendation': full_recommendation,
        'diagnoses': diagnoses,
        'detailed_answers': answers
    })


@app.route('/hormone_blood_test', methods=['GET', 'POST'])
def hormone_blood_test():
    form = HormonesBloodForm()

    if request.method == 'GET' or not form.validate_on_submit():
        return jsonify(form.errors), 400

    agent_output = ag.hormones_blood(tsh=form.tsh.data, fsh=form.fsh.data, lh=form.lh.data)

    if not ag.success():
        return jsonify({
            'status': 'error',
            'message': 'Agent error'
        }), 500

    result = BloodSerializer().load(agent_output)

    if not result.get("message"):
        return jsonify({
            'status': 'success',
            'result': 'Норма',
            'recommendation': 'Все показатели в пределах нормы'
        })

    if result.get("message") == "Not Found":
        return jsonify({
            'status': 'error',
            'message': 'Agent says: Not Found.'
        }), 404

    diagnoses = result.get("message", [])
    answers = [endocrine_system_json.get(disease, {
        'result': 'Неизвестное состояние',
        'recommendation': 'Требуется консультация специалиста'
    }) for disease in diagnoses]

    full_result = ", ".join([answer['result'] for answer in answers])
    full_recommendation = "\n".join([answer['recommendation'] for answer in answers])

    if current_user.is_authenticated:
        create_model_instance(
            Diagnostic,
            type="Анализ крови на гормоны",
            user_id=current_user.id,
            selected={
                "Тиреотропный гормон": form.tsh.data,
                "Фолликулостимулирующий гормон": form.fsh.data,
                "Лютеинизирующий гормон": form.lh.data,
            },
            result={answer['result']: answer['recommendation'] for answer in answers},
        )

    return jsonify({
        'status': 'success',
        'result': full_result,
        'recommendation': full_recommendation,
        'diagnoses': diagnoses,
        'detailed_answers': answers
    })


@app.route('/diagnose_symptoms', methods=['POST'])
def diagnose_symptoms():
    # Get symptoms from request
    data = request.get_json()
    general_symptoms = data.get('general_symptoms', [])
    local_symptoms = data.get('local_symptoms', [])
    dont_save = data.get('dont_save', False)

    symptoms = general_symptoms + local_symptoms
    print(symptoms)

    agent_output = ag.diagnosis(symptoms)
    print(agent_output)

    if not ag.success():
        return jsonify({
            'status': 'error',
            'message': 'Agent error'
        }), 500

    result = BloodListOfDictsSerializer().load(agent_output)

    if result.get("message") == "Not Found":
        return jsonify({
            'status': 'error',
            'message': 'Agent says: Not Found.'
        }), 404

    diagnoses = result.get("message", [])
    print(diagnoses)
    diagnoses = [
        {
            "disease": diseases_json.get(disease["disease"]).get("result") if diseases_json.get(disease["disease"]) else disease["disease"],
            "probability": disease["probability"],
            "specialist": diseases_json.get(disease["disease"]).get("specialist") if diseases_json.get(disease["disease"]) else None,
        } for disease in diagnoses]

    if current_user.is_authenticated and not dont_save:
        create_model_instance(
            Diagnostic,
            type="Диагностика",
            user_id=current_user.id,
            selected={str(i+1): symptoms_json.get(symptom) for i, symptom in enumerate(symptoms)},
            result={
                "Заболевания": ", ".join(disease["disease"] for disease in diagnoses),
                "Рекомендуемые специалисты": ", ".join(str(disease["specialist"]) for disease in diagnoses),
            },
        )

    return jsonify({
        'status': 'success',
        'results': diagnoses,
        'disclaimer': 'Результаты данной диагностики не являются достоверным медицинским заключением, для этого необходимо обратиться к врачу в медицинском учреждении.'
    })


@app.route('/blood_test')
def blood_test():
    hormones_form: HormonesBloodForm = HormonesBloodForm()
    common_form: CommonBloodForm = CommonBloodForm()
    micronutrients_form: MicronutrientsBloodForm = MicronutrientsBloodForm()
    vitamin_form: VitaminBloodForm = VitaminBloodForm()
    return render_template(
        'bloodTest2.html',
        hormones_form=hormones_form,
        common_form=common_form,
        micronutrients_form=micronutrients_form,
        vitamin_form=vitamin_form,
    )


@app.route('/diagnostic_history')
@login_required
def diagnostic_history():
    diagnostics = selectors.select_diagnostics_by_user_id(current_user)

    return render_template('diagnosticHistory.html', diagnostics=diagnostics)


@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    # template = 'recommendation.html'
    template = 'healthRecommendations.html'
    form: RecommendationForm = RecommendationForm()
    if not form.validate_on_submit():
        return render_form_template(form, template)

    agent_output = ag.rec(form.query.data)
    if not ag.success():
        return render_form_flash_template(form, template, message='Agent error')
    result = ApiSerializer().load(agent_output)

    if result.get("message") == "Not Found":
        return render_form_flash_template(form, template, message='Agent says: Not Found.')

    if current_user.patient:
        user = current_user.patient
    else:
        user = current_user.doctor

    return render_template(
        template,
        name=user.firstname,
        surname=user.surname,
        form=form,
        answer=result.get("message"),
    )


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/doctor_appointments')
@login_required
@doctor_required
def doctor_appointments():
    template = 'doctorAppointments.html'
    form: DoctorScheduleForm = DoctorScheduleForm()

    appointments_by_day, appointments_times, days = services.get_appointments()

    if current_user.patient:
        user = current_user.patient
    else:
        user = current_user.doctor
    return render_template(
        template,
        name=user.firstname,
        surname=user.surname,
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

    if current_user.patient:
        user = current_user.patient
    else:
        user = current_user.doctor
    return render_template(
        template,
        name=user.firstname,
        surname=user.surname,
        patient_appointments=patient_appointments,
    )


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

    if current_user.patient:
        user = current_user.patient
    else:
        user = current_user.doctor
    return render_template(
        template,
        name=user.firstname,
        surname=user.surname,
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

    # agent_output = ag.auth(form.username.data, form.password.data)
    # if not ag.success():
    #     return render_form_flash_template(form, template, message='Agent error')
    # result = LoginSerializer().load(agent_output)
    #
    # if result.get("status") != "valid":
    #     return render_form_flash_template(form, template, message='Agent says: Invalid username or password.')

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
        User,
        commit=False,
        username=form.email.data,
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
        city=form.city.data,
        street=form.street.data,
        building=form.building.data,
        latitude=form.latitude.data,
        longitude=form.longitude.data,
        practice_profile=form.practice_profile.data,
        phone=form.phone.data,
        photo_path=filename,
        user=new_user,
    )

    agent_output = ag.reg(form.email.data, form.password.data)
    if not ag.success():
        return render_form_flash_template(form, template, message='Agent error')
    result = RegisterSerializer().load(agent_output)
    print(result)

    if result.get("status") == "exists":
        return render_form_flash_template(form, template, message='Agent says: User exists.')
    if result.get("status") == "created":
        return redirect(url_for('login'))
    return render_form_flash_template(form, template, message='Agent error')


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
        User,
        commit=False,
        username=form.email.data,
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

    agent_output = ag.reg(form.email.data, form.password.data)
    if not ag.success():
        return render_form_flash_template(form, template, message='Agent error')
    result = RegisterSerializer().load(agent_output)
    print(result)

    if result.get("status") == "exists":
        return render_form_flash_template(form, template, message='Agent says: User exists.')
    if result.get("status") == "created":
        return redirect(url_for('login'))
    return render_form_flash_template(form, template, message='Agent error')


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return User.query.get(user_id)


@app.route('/diagnose', methods=['POST'])
def diagnose():
    symptoms = request.json.get('symptoms', [])
    possible_diseases = disease_definer.get_possible_disease(symptoms)

    return jsonify(possible_diseases)
