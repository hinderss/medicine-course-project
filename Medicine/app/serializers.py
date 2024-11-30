from app import ma
from app.models import Doctor


class DoctorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Doctor
        include_fk = True


doctors_schema = DoctorSchema(many=True)
