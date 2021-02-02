from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from config import db
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
metadata = Base.metadata


class Patient(db.Model):
    __tablename__ = 'Patient'

    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column('fname_tx', db.String(100), nullable=False)
    last_name = db.Column('lname_tx', db.String(100), nullable=False)
    email_tx = db.Column(db.String(100), unique=True, nullable=False)
    ic_card_tx = db.Column(db.String(20), nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)
    Appointments = db.relationship('Appointment', backref='Patient', lazy=True)
    Immunizations = db.relationship('Immunization', backref='Patient', lazy=True)

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email_tx = data.get('email')
        self.ic_card_tx = data.get('ic_card')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.update_dt = func.now()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Patient.query.all()

    @staticmethod
    def get_one(patient_id):
        return Patient.query.get(patient_id)

    @staticmethod
    def get_by_email(patient_email):
        return Patient.query.get(email_tx=patient_email)


class Practitioner(db.Model):
    __tablename__ = 'Practitioner'

    practitioner_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    ic_card_tx = db.Column(db.String(20), nullable=False)
    doctor_fl = db.Column(db.Boolean())
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)
    Appointments = db.relationship('Appointment', backref='Practitioner', lazy=True)
    Immunizations = db.relationship('Immunization', backref='Practitioner', lazy=True)

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email_address = data.get('email')
        self.ic_card_tx = data.get('ic_card')
        self.doctor_fl = data.get('is_doctor')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.update_dt = func.now()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Practitioner.query.all()

    @staticmethod
    def get_one(practitioner_id):
        return Practitioner.query.get(practitioner_id)

    @staticmethod
    def get_by_email(practitioner_email):
        return Practitioner.query.get(email_address=practitioner_email)


class Provider(db.Model):
    __tablename__ = 'Provider'

    provider_id = db.Column(db.Integer, primary_key=True)
    name_tx = db.Column(db.String(100), nullable=False)
    site_admin_email = db.Column(db.String(100), unique=True, nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, data):
        self.name_tx = data.get('name')
        self.author = data.get('site_admin_email')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.update_dt = func.now()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Provider.query.all()

    @staticmethod
    def get_one(provider_id):
        return Provider.query.get(provider_id)

    @staticmethod
    def get_by_email(provider_email):
        return Provider.query.get(site_admin_email=provider_email)


class Vaccine(db.Model):
    __tablename__ = 'Vaccine'

    vaccine_id = db.Column(db.Integer, primary_key=True)
    name_tx = db.Column(db.String(100), nullable=False)
    doses_required = db.Column(db.Integer, nullable=False)
    description_tx = db.Column(db.Text, nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)
    Immunizations = db.relationship('Immunization', backref='Vaccine', lazy=True)

    def __init__(self, data):
        self.name_tx = data.get('vaccine_name')
        self.doses_required = data.get('doses_required')
        self.description_tx = data.get('description')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.update_dt = func.now()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Vaccine.query.all()

    @staticmethod
    def get_one(vaccine_id):
        return Vaccine.query.get(vaccine_id)


class Appointment(db.Model):
    __tablename__ = 'Appointment'

    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'), nullable=False)
    scheduled_by_practitioner_id = db.Column(db.Integer, db.ForeignKey('Practitioner.practitioner_id'), nullable=False)
    appointment_date = db.Column(db.DateTime(timezone=True), nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, data):
        self.patient_id = data.get('patient_id')
        self.scheduled_by_practitioner_id = data.get('practitioner_id')
        self.appointment_date = data.get('appointment_date')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.update_dt = func.now()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Appointment.query.all()

    @staticmethod
    def get_one(appointment_id):
        return Appointment.query.get(appointment_id)


class Immunization(db.Model):
    __tablename__ = 'Immunization'

    immunization_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('Practitioner.practitioner_id'), nullable=False)
    vaccine_id = db.Column(db.Integer, db.ForeignKey('Vaccine.vaccine_id'), nullable=False)
    administered_dt = db.Column(db.DateTime(timezone=True), nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, data):
        self.patient_id = data.get('patient_id')
        self.practitioner_id = data.get('practitioner_id')
        self.vaccine_id = data.get('vaccine_id')
        self.administered_dt = data.get('administered_date')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.update_dt = func.now()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Immunization.query.all()

    @staticmethod
    def get_one(immunization_id):
        return Immunization.query.get(immunization_id)


class Permissions(db.Model):
    __tablename__ = 'Permissions'

    permissions_id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.String(100), nullable=False)
    Permission = db.relationship('RolePermission', backref='Permissions', lazy=True)

    @staticmethod
    def get_all():
        return Permissions.query.all()

    @staticmethod
    def get_permissions(permission_ids):
        return Permissions.query.filter(Permissions.permissions_id.in_(permission_ids)).values('permission')


class RolePermission(db.Model):
    __tablename__ = 'RolePermission'

    role_permission_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('Permissions.permissions_id'), nullable=False)
    Role = db.relationship('Users', backref='RolePermission', lazy=True)

    @staticmethod
    def get_all():
        return RolePermission.query.all()

    @staticmethod
    def get_permissions(role_id):
        return RolePermission.query.filter(role_id=role_id).values('permission_id')


class Users(db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    hash_password = db.Column(db.Text, nullable=False)
    security_role = db.Column(db.Integer, db.ForeignKey('RolePermission.role_id'), nullable=False)
    token = db.Column(db.Text, nullable=True)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    @staticmethod
    def get_user_based_on_email(user_email):
        return Users.query.get(user_email=user_email)
