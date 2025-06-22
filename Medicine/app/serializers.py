from marshmallow import Schema, fields, validate

from app import ma
from app.models import Doctor


class DoctorSchema(ma.SQLAlchemyAutoSchema):
    address = fields.Method("get_address")

    def get_address(self, obj):
        return obj.address

    class Meta:
        model = Doctor
        include_fk = True


doctors_schema = DoctorSchema(many=True)


class Error(Schema):
    error = fields.Str(required=False)
    message = fields.Str(required=False, allow_none=True)
    description = fields.Dict(required=False)
    details = fields.Field(required=False)


class ApiSerializer(Schema):
    message = fields.Str(required=False, allow_none=True)


class BloodSerializer(Schema):
    message = fields.List(fields.Str, required=False, allow_none=True)


class BloodListOfDictsSerializer(Schema):
    message = fields.List(fields.Dict, required=False, allow_none=True)


class LoginSerializer(ApiSerializer):
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["valid", "invalid"]),
    )


class RegisterSerializer(ApiSerializer):
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["created", "exists"]),
    )

