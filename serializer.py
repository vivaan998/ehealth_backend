from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow.validate import Range


class BaseSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1))
    last_name = fields.String(required=True, validate=validate.Length(min=1))
    email_tx = fields.Email(required=True, validate=validate.Length(min=1))
    ic_card_tx = fields.String(required=True, validate=validate.Length(max=20))
    active_fl = fields.Boolean()
    created_dt = fields.DateTime()
    update_dt = fields.DateTime()


class NewSchema(Schema):
    name_tx = fields.String(required=True, validate=validate.Length(min=1))
    active_fl = fields.Boolean()
    created_dt = fields.DateTime()
    update_dt = fields.DateTime()


class NewBaseSchema(Schema):
    patient_id = fields.Integer(strict=True, required=True)
    practitioner_id = fields.Integer(strict=True, required=True)
    provider_id = fields.Integer(strict=True, required=True)
    active_fl = fields.Boolean()
    created_dt = fields.DateTime()
    update_dt = fields.DateTime()


class PatientSchema(BaseSchema):
    patient_id = fields.Int(dump_only=True)
    practitioner_id = fields.Integer(strict=True, required=True)
    provider_id = fields.Integer(strict=True, required=True)


class PractitionerSchema(BaseSchema):
    practitioner_id = fields.Int(dump_only=True)
    provider_id = fields.Integer(strict=True, required=True)
    doctor_fl = fields.Boolean()


class ProviderSchema(NewSchema):
    provider_id = fields.Int(dump_only=True)
    site_admin_email = fields.Email(required=True, validate=validate.Length(min=1))


class VaccineSchema(NewSchema):
    vaccine_id = fields.Int(dump_only=True)
    doses_required = fields.Integer(strict=True, required=True)
    description_tx = fields.String(required=True, validate=validate.Length(min=1))


class AppointmentSchema(NewBaseSchema):
    appointment_id = fields.Int(dump_only=True)
    appointment_date = fields.DateTime()


class ImmunizationSchema(NewBaseSchema):
    immunization_id = fields.Int(dump_only=True)
    vaccine_id = fields.Integer(strict=True, required=True)
    administered_dt = fields.DateTime()


class UsersSchema(Schema):
    user_id = fields.Int(dump_only=True)
    user_email = fields.Email(strict=True, required=True)
    hash_password = fields.String(required=True, validate=validate.Length(min=1))
    security_role = fields.Integer(required=True, strict=True)
