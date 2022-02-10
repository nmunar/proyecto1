import enum
from xmlrpc.client import DateTime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
from dateutil import parser
from marshmallow_enum import EnumField
from flask_cors.extension import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

api = Api(app)
CORS(app)