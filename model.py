import datetime
from collections import OrderedDict

import sqlalchemy.orm.exc as ex
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from config import db
from sqlalchemy import or_, desc, asc, extract
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()
metadata = Base.metadata
PER_PAGE = 10


class Patient(db.Model):
    __tablename__ = 'Patient'

    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column('fname_tx', db.String(100), nullable=False)
    last_name = db.Column('lname_tx', db.String(100), nullable=False)
    email_tx = db.Column(db.String(100), unique=True, nullable=False)
    ic_card_tx = db.Column(db.String(20), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('Practitioner.practitioner_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.provider_id'), nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    Appointments = db.relationship('Appointment', backref='Patient', lazy="joined")
    Immunizations = db.relationship('Immunization', backref='Patient', lazy="joined")
    Vital = db.relationship('Vitals', backref='Patient', lazy="joined")

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email_tx = data.get('email_tx')
        self.provider_id = data.get('provider_id')
        self.practitioner_id = data.get('practitioner_id')
        self.ic_card_tx = data.get('ic_card_tx')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 0
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def get_all(page, search):
        if not search:
            return Patient.query.filter(Patient.active_fl == True).order_by(desc(Patient.created_dt)). \
                paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Patient.query.filter(or_(func.lower(Patient.first_name).contains(search),
                                            func.lower(Patient.last_name).contains(search),
                                            func.lower(Patient.email_tx).contains(search),
                                            func.lower(Patient.ic_card_tx).contains(search)),
                                        Patient.active_fl == True).order_by(desc(Patient.created_dt)). \
                paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get_patient_by_providers(page, search, provider_id):
        if not search:
            return Patient.query.filter(Patient.provider_id == provider_id, Patient.active_fl == True). \
                order_by(desc(Patient.created_dt)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Practitioner.query.filter(or_(func.lower(Patient.first_name).contains(search),
                                                 func.lower(Patient.last_name).contains(search),
                                                 func.lower(Patient.email_tx).contains(search),
                                                 func.lower(Patient.ic_card_tx).contains(search)),
                                             Patient.provider_id == provider_id, Patient.active_fl == True). \
                order_by(desc(Patient.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get_patient_by_practitioners(page, search, practitioner_id):
        if not search:
            return Patient.query.filter(Patient.practitioner_id == practitioner_id, Patient.active_fl == True). \
                order_by(desc(Patient.created_dt)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Practitioner.query.filter(or_(func.lower(Patient.first_name).contains(search),
                                                 func.lower(Patient.last_name).contains(search),
                                                 func.lower(Patient.email_tx).contains(search),
                                                 func.lower(Patient.ic_card_tx).contains(search)),
                                             Patient.practitioner_id == practitioner_id, Patient.active_fl == True). \
                order_by(desc(Patient.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get(practitioner_id):
        return Patient.query.filter(Patient.practitioner_id == practitioner_id, Patient.active_fl == True).all()

    @staticmethod
    def get_one(patient_id):
        return Patient.query.get(patient_id)

    @staticmethod
    def get_by_email(patient_email):
        return Patient.query.filter(Patient.email_tx == patient_email, Patient.active_fl == True).all()


class Practitioner(db.Model):
    __tablename__ = 'Practitioner'

    practitioner_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_tx = db.Column(db.String(100), unique=True, nullable=False)
    ic_card_tx = db.Column(db.String(20), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.provider_id'), nullable=False)
    doctor_fl = db.Column(db.Boolean())
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    Appointments = db.relationship('Appointment', backref='Practitioner', lazy="joined")
    Immunizations = db.relationship('Immunization', backref='Practitioner', lazy="joined")
    Patients = db.relationship('Patient', backref='Practitioner', lazy='joined')
    Vital = db.relationship('Vitals', backref='Practitioner', lazy="joined")

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email_tx = data.get('email_tx')
        self.provider_id = data.get('provider_id')
        self.ic_card_tx = data.get('ic_card_tx')
        self.doctor_fl = data.get('doctor_fl')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 0
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def get_all(page, search):
        if not search:
            return Practitioner.query.filter(Practitioner.active_fl == True).order_by(asc(Practitioner.first_name)). \
                paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Practitioner.query.filter(or_(func.lower(Practitioner.first_name).contains(search),
                                                 func.lower(Practitioner.last_name).contains(search),
                                                 func.lower(Practitioner.email_tx).contains(search),
                                                 func.lower(Practitioner.ic_card_tx).contains(search)),
                                             Practitioner.active_fl == True).order_by(asc(Practitioner.first_name)). \
                paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get_practitioners_by_providers(page, search, provider_id):
        if not search:
            return Practitioner.query.filter(Practitioner.provider_id == provider_id, Practitioner.active_fl == True). \
                order_by(asc(Practitioner.first_name)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Practitioner.query.filter(or_(func.lower(Practitioner.first_name).contains(search),
                                                 func.lower(Practitioner.last_name).contains(search),
                                                 func.lower(Practitioner.email_tx).contains(search),
                                                 func.lower(Practitioner.ic_card_tx).contains(search)),
                                             Practitioner.provider_id == provider_id, Practitioner.active_fl == True). \
                order_by(asc(Practitioner.first_name)).paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get(provider_id):
        return Practitioner.query.filter(Practitioner.provider_id == provider_id, Practitioner.active_fl == True).all()

    @staticmethod
    def get_one(practitioner_id):
        return Practitioner.query.get(practitioner_id)

    @staticmethod
    def get_by_email(practitioner_email):
        return Practitioner.query.filter(Practitioner.email_tx == practitioner_email, Practitioner.active_fl == True). \
            all()


class Provider(db.Model):
    __tablename__ = 'Provider'

    provider_id = db.Column(db.Integer, primary_key=True)
    name_tx = db.Column(db.String(100), nullable=False)
    site_admin_email = db.Column(db.String(100), unique=True, nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    Practitioners = db.relationship('Practitioner', backref='Provider', lazy=True)
    Patients = db.relationship('Patient', backref='Provider', lazy=True)
    Appointments = db.relationship('Appointment', backref='Provider', lazy="joined")
    Immunizations = db.relationship('Immunization', backref='Provider', lazy="joined")
    Vital = db.relationship('Vitals', backref='Provider', lazy="joined")

    def __init__(self, data):
        self.name_tx = data.get('name_tx')
        self.site_admin_email = data.get('site_admin_email')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 0
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def get_all(page, search):
        if not search:
            return Provider.query.filter(Provider.active_fl == True).order_by(asc(Provider.name_tx)).paginate(
                int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Provider.query.filter(or_(func.lower(Provider.name_tx).contains(search),
                                             func.lower(Provider.site_admin_email).contains(search)),
                                         Provider.active_fl == True).order_by(asc(Provider.name_tx)). \
                paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get_one(provider_id):
        return Provider.query.get(provider_id)

    @staticmethod
    def get():
        return Provider.query.filter(Provider.active_fl == True).all()

    @staticmethod
    def get_provider():
        return Provider.query.all()

    @staticmethod
    def get_by_email(provider_email):
        return Provider.query.filter(Provider.site_admin_email == provider_email, Provider.active_fl == True).all()


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
        self.name_tx = data.get('name_tx')
        self.doses_required = data.get('doses_required')
        self.description_tx = data.get('description_tx')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 0
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def get_all(page, search):
        if not search:
            return Vaccine.query.filter(Vaccine.active_fl == True).order_by(asc(Vaccine.name_tx)). \
                paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            return Vaccine.query.filter(or_(func.lower(Vaccine.name_tx).contains(search),
                                            func.lower(Vaccine.description_tx).contains(search)),
                                        Vaccine.active_fl == True).order_by(asc(Vaccine.name_tx)). \
                paginate(int(page), PER_PAGE, error_out=True)

    @staticmethod
    def get_one(vaccine_id):
        return Vaccine.query.get(vaccine_id)

    @staticmethod
    def get():
        return Vaccine.query.filter(Vaccine.active_fl == True).all()


class Appointment(db.Model):
    __tablename__ = 'Appointment'

    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('Practitioner.practitioner_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.provider_id'), nullable=False)
    appointment_date = db.Column(db.DateTime(timezone=True), nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, data):
        self.patient_id = data.get('patient_id')
        self.practitioner_id = data.get('practitioner_id')
        self.provider_id = data.get('provider_id')
        self.appointment_date = data.get('appointment_date')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 0
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def get_all(page, search):
        if not search:
            query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
                join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Appointment.provider_id == Provider.provider_id).filter(Appointment.active_fl == True). \
                order_by(asc(Appointment.appointment_date)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
                join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Appointment.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search),
                           func.lower(Provider.name_tx).contains(search),
                           func.lower(Practitioner.first_name).contains(search)),
                       Appointment.active_fl == True).order_by(asc(Appointment.appointment_date)). \
                paginate(int(page), PER_PAGE, error_out=True)
        if query.items:
            return [{
                "appointment_id": model.appointment_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "appointment_date": model.appointment_date.strftime("%x"),
                "appointment_time": model.appointment_date.strftime("%X"),
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "created_at": model.created_dt.strftime("%c")
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_appointment_by_providers(page, search, provider_id):
        if not search:
            query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
                join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Appointment.provider_id == Provider.provider_id). \
                filter(Appointment.active_fl == True, Appointment.provider_id == provider_id). \
                order_by(asc(Appointment.appointment_date)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
                join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Appointment.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search),
                           func.lower(Practitioner.first_name).contains(search)),
                       Appointment.active_fl == True, Appointment.provider_id == provider_id). \
                order_by(asc(Appointment.appointment_date)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "appointment_id": model.appointment_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "appointment_date": model.appointment_date.strftime("%x"),
                "appointment_time": model.appointment_date.strftime("%X"),
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "created_at": model.created_dt.strftime("%c")
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_appointment_by_practitioners(page, search, practitioner_id):
        if not search:
            query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
                join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Appointment.provider_id == Provider.provider_id). \
                filter(Appointment.active_fl == True, Appointment.practitioner_id == practitioner_id). \
                order_by(asc(Appointment.appointment_date)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
                join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Appointment.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search)),
                       Appointment.active_fl == True, Appointment.practitioner_id == practitioner_id). \
                order_by(asc(Appointment.appointment_date)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "appointment_id": model.appointment_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "appointment_date": model.appointment_date.strftime("%x"),
                "appointment_time": model.appointment_date.strftime("%X"),
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "created_at": model.created_dt.strftime("%c")
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_appointment_by_patients(page, patient_id):
        query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id). \
            join(Practitioner, Appointment.practitioner_id == Practitioner.practitioner_id). \
            join(Provider, Appointment.provider_id == Provider.provider_id). \
            filter(Appointment.active_fl == True, Appointment.patient_id == patient_id). \
            order_by(asc(Appointment.appointment_date)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "appointment_id": model.appointment_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "appointment_date": model.appointment_date.strftime("%x"),
                "appointment_time": model.appointment_date.strftime("%X"),
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "created_at": model.created_dt.strftime("%c")
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_one(appointment_id):
        return Appointment.query.get(appointment_id)


class Immunization(db.Model):
    __tablename__ = 'Immunization'

    immunization_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('Practitioner.practitioner_id'), nullable=False)
    vaccine_id = db.Column(db.Integer, db.ForeignKey('Vaccine.vaccine_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.provider_id'), nullable=False)
    administered_dt = db.Column(db.DateTime(timezone=True), nullable=False)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, data):
        self.patient_id = data.get('patient_id')
        self.practitioner_id = data.get('practitioner_id')
        self.provider_id = data.get('provider_id')
        self.vaccine_id = data.get('vaccine_id')
        self.administered_dt = data.get('administered_dt')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 0
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def provider_immunization_chart():
        query = db.session.query(Immunization.provider_id, func.count(Immunization.immunization_id)). \
            group_by(Immunization.provider_id).all()

        providers = [provider.provider_id for provider in Provider.get_provider()]
        result = []

        for q in query:
            result.append({
                "provider_id": q[0],
                "provider": Provider.get_one(q[0]).name_tx,
                "total_immunizations": q[1]
            })
            providers.remove(q[0])

        for provider in providers:
            result.append({
                "provider_id": provider,
                "provider": Provider.get_one(provider).name_tx,
                "total_immunizations": 0
            })
        result.sort(key=lambda x: x['provider'])
        return result

    @staticmethod
    def monthly_immunization_chart():
        date_today = datetime.datetime.now()
        expiry = date_today - datetime.timedelta(days=365)
        calendar_dict = OrderedDict(((expiry + datetime.timedelta(_)).strftime("%Y-%b"), 0)
                                    for _ in range((date_today - expiry).days))

        query = db.session.query(extract('month', Immunization.administered_dt),
                                 extract('year', Immunization.administered_dt),
                                 func.count(Immunization.immunization_id)). \
            filter(Immunization.administered_dt >= expiry). \
            group_by(extract('month', Immunization.administered_dt),
                     extract('year', Immunization.administered_dt)).all()

        result = []
        for q in query:
            month = datetime.date(year=int(q[1]), month=int(q[0]), day=1).strftime("%Y-%b")
            result.append({
                "month": month,
                "total_immunizations": int(q[2])
            })
            calendar_dict.pop(month)

        for key, value in calendar_dict.items():
            result.append({
                "month": key,
                "total_immunizations": value
            })

        result.sort(key=lambda x: datetime.datetime.strptime(x['month'], '%Y-%b'))
        return result

    @staticmethod
    def get_all(page, search):
        if not search:
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id).filter(Immunization.active_fl == True). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search),
                           func.lower(Provider.name_tx).contains(search),
                           func.lower(Practitioner.first_name).contains(search),
                           func.lower(Vaccine.name_tx).contains(search)),
                       Immunization.active_fl == True).order_by(desc(Immunization.created_dt)). \
                paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "immunization_id": model.immunization_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "vaccine_id": model.vaccine_id,
                "administered_dt": model.administered_dt,
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "vaccine": model.Vaccine.name_tx,
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_one(immunization_id):
        return Immunization.query.get(immunization_id)

    @staticmethod
    def get_immunization_by_providers(page, search, provider_id):
        if not search:
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(Immunization.active_fl == True, Immunization.provider_id == provider_id). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search),
                           func.lower(Practitioner.first_name).contains(search),
                           func.lower(Vaccine.name_tx).contains(search)),
                       Immunization.active_fl == True, Immunization.provider_id == provider_id). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "immunization_id": model.immunization_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "vaccine_id": model.vaccine_id,
                "administered_dt": model.administered_dt,
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "vaccine": model.Vaccine.name_tx,
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_immunization_by_practitioners(page, search, practitioner_id):
        if not search:
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(Immunization.active_fl == True, Immunization.practitioner_id == practitioner_id). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search),
                           func.lower(Vaccine.name_tx).contains(search)),
                       Immunization.active_fl == True, Immunization.practitioner_id == practitioner_id). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "immunization_id": model.immunization_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "vaccine_id": model.vaccine_id,
                "administered_dt": model.administered_dt,
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "vaccine": model.Vaccine.name_tx,
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_immunization_by_patients(page, patient_id):
        query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
            join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
            join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
            join(Provider, Immunization.provider_id == Provider.provider_id). \
            filter(Immunization.active_fl == True, Immunization.patient_id == patient_id). \
            order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "immunization_id": model.immunization_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "vaccine_id": model.vaccine_id,
                "administered_dt": model.administered_dt,
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "vaccine": model.Vaccine.name_tx,
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_vaccines_administered(page, search, vaccine_id):
        if not search:
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(Immunization.vaccine_id == vaccine_id). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)
        else:
            search = search.lower()
            query = db.session.query(Immunization).join(Patient, Immunization.patient_id == Patient.patient_id). \
                join(Vaccine, Immunization.vaccine_id == Vaccine.vaccine_id). \
                join(Practitioner, Immunization.practitioner_id == Practitioner.practitioner_id). \
                join(Provider, Immunization.provider_id == Provider.provider_id). \
                filter(or_(func.lower(Patient.first_name).contains(search),
                           func.lower(Practitioner.first_name).contains(search),
                           func.lower(Provider.name_tx).contains(search)),
                       Immunization.vaccine_id == vaccine_id). \
                order_by(desc(Immunization.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "immunization_id": model.immunization_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "vaccine_id": model.vaccine_id,
                "administered_dt": model.administered_dt,
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
                "vaccine": model.Vaccine.name_tx,
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0


class Permissions(db.Model):
    __tablename__ = 'Permissions'

    permissions_id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    Permission = db.relationship('RolePermission', backref='Permissions', lazy="joined")


class RolePermission(db.Model):
    __tablename__ = 'RolePermission'

    role_permission_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('Permissions.permissions_id'), nullable=False)

    @staticmethod
    def get_permissions(role_id):
        query = db.session.query(RolePermission).join(Permissions).filter(RolePermission.role_id == role_id)
        return [{
            "title": model.Permissions.permission,
            "icon": model.Permissions.icon,
            "url": model.Permissions.url
        } for model in query]


class Users(db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    hash_password = db.Column(db.Text, nullable=False)
    security_role = db.Column(db.Integer, nullable=False)

    def __init__(self, data):
        self.user_email = data.get('user_email')
        self.hash_password = generate_password_hash(data.get('hash_password'))
        self.security_role = data.get('security_role')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.hash_password, password)

    @staticmethod
    def get_user(user_email):
        user = Users.query.filter(Users.user_email == user_email).all()
        if user:
            if user[0].security_role == 0:
                if Patient.get_by_email(user[0].user_email):
                    return user[0]
            elif user[0].security_role == 10:
                if Practitioner.get_by_email(user[0].user_email):
                    return user[0]
            elif user[0].security_role == 50:
                if Provider.get_by_email(user[0].user_email):
                    return user[0]
            else:
                return user[0]
        else:
            return None

    @staticmethod
    def get_name(role, email):
        try:
            if role == 50:
                provider = Provider.get_by_email(email)[0]
                name = provider.name_tx
                designation = 'Provider'
                user_id = provider.provider_id
                practitioner_name = None
                provider_name = None
            elif role == 10:
                practitioner = Practitioner.get_by_email(email)[0]
                name = practitioner.first_name + " " + practitioner.last_name
                designation = 'Practitioner'
                user_id = practitioner.practitioner_id
                practitioner_name = None
                provider_name = Provider.get_one(practitioner.provider_id).name_tx
            elif role == 0:
                patient = Patient.get_by_email(email)[0]
                name = patient.first_name + " " + patient.last_name
                designation = 'Patient'
                user_id = patient.patient_id
                temp = Practitioner.get_one(patient.practitioner_id)
                practitioner_name = temp.first_name + " " + temp.last_name
                provider_name = Provider.get_one(patient.provider_id).name_tx
            else:
                name = 'Super User'
                designation = 'Admin'
                user_id = 1
                practitioner_name = None
                provider_name = None
            return name, designation, user_id, practitioner_name, provider_name
        except ex.NoResultFound:
            raise Exception('No user found')


class Logs(db.Model):
    __tablename__ = 'Logs'

    log_id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.Text, nullable=False)
    trace = db.Column(db.Text, nullable=False)
    method = db.Column(db.String(10), nullable=False)
    error_code = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, data):
        self.msg = data.get('message')
        self.trace = data.get('traceback')
        self.method = data.get('method')
        self.error_code = data.get('error_code')

    def save(self):
        db.session.add(self)
        db.session.commit()


class Vitals(db.Model):
    __tablename__ = 'Vitals'

    vital_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('Practitioner.practitioner_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.provider_id'), nullable=False)
    bp_systolic = db.Column(db.String(10), nullable=False)
    bp_diastolic = db.Column(db.String(10), nullable=False)
    body_temp = db.Column(db.String(10), nullable=False)
    heart_rate = db.Column(db.String(10), nullable=False)
    memo = db.Column(db.String(500), nullable=True)
    active_fl = db.Column(db.Boolean(), default=1)
    created_dt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_dt = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, data):
        self.patient_id = data.get('patient_id')
        self.provider_id = data.get('provider_id')
        self.practitioner_id = data.get('practitioner_id')
        self.bp_systolic = data.get('bp_systolic')
        self.body_temp = data.get('body_temp')
        self.bp_diastolic = data.get('bp_diastolic')
        self.heart_rate = data.get('heart_rate')
        self.memo = data.get('memo')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.active_fl = 1
        self.update_dt = func.now()
        db.session.commit()

    @staticmethod
    def get_vital_by_patients(page, patient_id):
        query = db.session.query(Vitals).join(Patient, Vitals.patient_id == Patient.patient_id). \
            join(Practitioner, Vitals.practitioner_id == Practitioner.practitioner_id). \
            join(Provider, Vitals.provider_id == Provider.provider_id). \
            filter(Vitals.active_fl == True, Vitals.patient_id == patient_id). \
            order_by(asc(Vitals.created_dt)).paginate(int(page), PER_PAGE, error_out=True)

        if query.items:
            return [{
                "vital_id": model.vital_id,
                "patient_id": model.patient_id,
                "practitioner_id": model.practitioner_id,
                "provider_id": model.provider_id,
                "bp_systolic": model.bp_systolic,
                "bp_diastolic": model.bp_diastolic,
                "body_temp": model.body_temp,
                "heart_rate": model.heart_rate,
                "memo": model.memo,
                "created_at": model.created_dt,
                "patient": model.Patient.first_name + " " + model.Patient.last_name,
                "practitioner": model.Practitioner.first_name + " " + model.Practitioner.last_name,
                "provider": model.Provider.name_tx,
            } for model in query.items], query.next_num, query.prev_num, query.total
        else:
            return [], None, None, 0

    @staticmethod
    def get_one(vital_id):
        return Vitals.query.get(vital_id)
