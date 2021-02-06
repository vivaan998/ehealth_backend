import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
basedir = os.path.abspath(os.path.dirname(__file__))

PROVIDER = 50
PRACTITIONER = 10
PATIENT = 0

POSTGRES_DB_URL = 'postgresql://postgres:attache123@attache-dev-db1.c00qcl0ls8g4.us-east-1.rds.amazonaws.com:5432' \
                  '/eHealth'
