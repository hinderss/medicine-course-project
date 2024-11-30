from flask import render_template, flash, jsonify

from app.exceptions import HttpJson404

from typing import Type

from app import db


def get_object_or_404(model, *, error_message=None, **kwargs):
    obj = model.query.filter_by(**kwargs).first()
    if obj is None:
        raise HttpJson404(error_message)
    return obj


def render_form_template(form, template=None):
    if template:
        return render_template(template, form=form)
    errors = {field: error for field, error in form.errors.items()}
    return jsonify(errors), 400


def render_form_flash_template(form, template, message):
    flash(message, 'error')
    return render_template(template, form=form)


def create_model_instance(model_class: Type[db.Model], *, commit: bool = True, **kwargs) -> db.Model:
    instance = model_class(**kwargs)
    db.session.add(instance)
    if commit:
        db.session.commit()
    return instance


def update_model_instance(instance: db.Model, *, commit: bool = True, **kwargs) -> db.Model:
    for key, value in kwargs.items():
        setattr(instance, key, value)
    if commit:
        db.session.commit()
    return instance


def delete_model_instance(instance: db.Model, *, commit: bool = True) -> None:
    db.session.delete(instance)
    if commit:
        db.session.commit()
