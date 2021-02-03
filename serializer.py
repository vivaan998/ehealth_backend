from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow.validate import Range


class PostPatient(Schema):
    patient_id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    duration = fields.Integer(strict=True, required=True, validate=[Range(min=1, error="Value must only be a positive "
                                                                                       "integer")])
    upload_time = fields.DateTime()
    updated_at = fields.DateTime()


class PodcastsSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    duration = fields.Integer(strict=True, required=True, validate=[Range(min=1, error="Value must only be a positive "
                                                                                       "integer")])
    host = fields.String(required=True, validate=validate.Length(min=1))
    participants = fields.List(fields.String())
    upload_time = fields.DateTime()
    updated_at = fields.DateTime()

    @validates("participants")
    def validate_participants(self, participants):
        if participants and len(participants) > 10:
            raise ValidationError("You can only have 10 participants")
        if participants:
            for participant in participants:
                if len(participant) > 100:
                    raise ValidationError("Participant's name cannot be greater than 100 characters")


class AudioBookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1))
    author = fields.String(required=True, validate=validate.Length(min=1))
    narrator = fields.String(required=True, validate=validate.Length(min=1))
    duration = fields.Integer(strict=True, required=True, validate=[Range(min=1, error="Value must only be a positive "
                                                                                       "integer")])
    upload_time = fields.DateTime()
    updated_at = fields.DateTime()
