from enum import unique
from http.client import ResponseNotReady
import os
from venv import create
from xmlrpc.client import DateTime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
from dateutil import parser
from gevent import config
from sqlalchemy import true
from werkzeug.utils import secure_filename
import flask_praetorian
from marshmallow_enum import EnumField
from flask_cors.extension import CORS
import json
import traceback
from flask_praetorian import auth_required, current_user
import uuid
from botocore.config import Config
from boto3.dynamodb.conditions import Key, Attr
import boto3
from botocore import UNSIGNED

# S3 configuration
my_config = Config(
    region_name='us-east-1',
)
s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.environ.get('AWS_ACCSESS_KEY_ID_DYNAMO'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCSESS_KEY_DYNAMO'),
                          aws_session_token=os.environ.get('AWS_SESSION_TOKEN_DYNAMO'), region_name=os.environ.get('REGION_NAME_DYNAMO'))
sqs = boto3.resource('sqs', region_name=os.environ.get('REGION_NAME_SQS'),
                     aws_access_key_id=os.environ.get(
                         'AWS_ACCSESS_KEY_ID_SQS'),
                     aws_secret_access_key=os.environ.get(
    'AWS_SECRET_ACCSESS_KEY_SQS'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN_SQS'))

queue = sqs.get_queue_by_name(QueueName='supervoices.fifo')

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'aac', 'ogg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a random string'
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:bd123@localhost:5432/concursos'
app.config['BROKER_URL'] = 'redis://localhost:6379/0'

CORS(app)
guard = flask_praetorian.Praetorian()

db = SQLAlchemy(app)

ma = Marshmallow(app)
# api = Api(app)

app.app_context().push()

extensions = ['wav', 'mp3', 'aac', 'ogg']

# Models


class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(220), nullable=0)
    apellidos = db.Column(db.String(220), nullable=0)
    email = db.Column(db.String(120), nullable=0, unique=1)
    contrasena = db.Column(db.String(300), nullable=0)
    # relaciones
    # concursos = db.relationship('Concurso', backref='administrador', lazy=1)

    @ property
    def rolenames(self):
        return []

    @ property
    def password(self):
        return self.contrasena

    @ classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @ classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @ property
    def identity(self):
        return self.id

    def is_valid(self):
        return True


table_administrador = dynamodb.Table('administrador')
table_concurso = dynamodb.Table('concurso')
table_voz = dynamodb.Table('voz')
table_archivo_voz = dynamodb.Table('archivo_voz')

# --------------------------- Schemas ---------------------------


class Administrador_Schema(ma.Schema):
    class Meta:
        fields = ("id", "nombres", "apellidos", "email")


schema_administrador = Administrador_Schema()
schema_administradores = Administrador_Schema(many=True)


# --------------------------- Routes ---------------------------

guard.init_app(app, Administrador)

# userAdmin


@ app.route('/api/login', methods=['POST'])
def login():
    req = json.loads(request.data)
    email = req.get('email', None)
    password = req.get('contrasena', None)
    admin = guard.authenticate(email, password)
    return jsonify({'access_token': guard.encode_jwt_token(admin)}), 200


@ app.route('/api/register', methods=['POST'])
def register():
    req = json.loads(request.data)
    nombres = req.get('nombres', None)
    apellidos = req.get('apellidos', None)
    email = req.get('email', None)
    contrasena = req.get('contrasena', None)

    if db.session.query(Administrador).filter_by(email=email).count() == 0:
        admin = Administrador(
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            contrasena=guard.hash_password(contrasena)
        )
        db.session.add(admin)
        db.session.commit()

        item = {
            'id': str(admin.id),
            'nombres': nombres,
            'apellidos': apellidos,
            'email': email
        }

        table_administrador.put_item(Item=item)

        return {"msg": "Usuario creado"}, 201

    else:
        return {"msg": "Correo ya registrado"}, 400

# Concursos


@ app.route('/api/concursos', methods=['GET', 'POST'])
@ auth_required
def concursos():
    user = current_user()
    if request.method == 'GET':
        response = table_concurso.scan(
            FilterExpression=Attr('administrador_id').eq(str(user.id)))
        return json.dumps(response['Items'])
    elif request.method == 'POST':
        req = json.loads(request.data)
        nombre = req.get('nombre', None)
        imagen = req.get('imagen', None)
        url = req.get('url', None)
        concursoURL = table_concurso.scan(
            FilterExpression=Attr('url').eq(url))['Items']

        if len(concursoURL) != 0:
            return {"error": "La URL del concurso ya se usa"}, 403
        fechaCreacion = datetime.now()
        fechaInicio = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        fechaFin = parser.parse(req.get('fechaFin', None), ignoretz=True)
        if(fechaInicio > fechaFin):
            return {"error": "La fecha de inicio es mayor a la de fin"}, 403
        valorPagar = req.get('valorPagar', None)
        guion = req.get('guion', None)
        recomendaciones = req.get('recomendaciones', None)
        administrador_id = str(user.id)

        id_concurso = str(uuid.uuid4())

        item = {
            'id': id_concurso,
            'nombre': nombre,
            'imagen': imagen,
            'url': url,
            'fechaCreacion': str(fechaCreacion),
            'fechaInicio': str(fechaInicio),
            'fechaFin': str(fechaFin),
            'valorPagar': valorPagar,
            'guion': guion,
            'recomendaciones': recomendaciones,
            'administrador_id': administrador_id

        }

        table_concurso.put_item(Item=item)

        return {"id": id_concurso, "fechaCreacion": str(fechaCreacion)}, 201


@ app.route('/api/concursos/<string:idConcurso>', methods=['GET', 'PUT', 'DELETE'])
@ auth_required
def concurso(idConcurso):
    user = current_user()
    concurso = table_concurso.query(
        KeyConditionExpression=Key('id').eq(idConcurso))['Items'][0]
    if str(user.id) != concurso['administrador_id']:
        return {"msg": "Solo se tiene acceso a sus propios concursos"}, 403

    if request.method == 'GET':
        return concurso
    elif request.method == 'PUT':
        req = json.loads(request.data)
        nombre = req.get('nombre', None)
        imagen = req.get('imagen', None)
        fechaInicio = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        fechaFin = parser.parse(req.get('fechaFin', None), ignoretz=True)
        if(fechaInicio > fechaFin):
            return {"error": "La fecha de inicio es mayor a la de fin"}, 403
        valorPagar = req.get('valorPagar', None)
        url = req.get('url', None)
        guion = req.get('guion', None)
        recomendaciones = req.get('recomendaciones', None)
        concursoURL = table_concurso.scan(
            FilterExpression=Attr('url').eq(url))['Items']

        if len(concursoURL) != 0:
            concursoURL = concursoURL[0]
            if concursoURL['id'] != idConcurso:
                return {"error": "La URL del concurso ya se usa"}, 403

        concurso['nombre'] = nombre
        concurso['imagen'] = imagen
        concurso['fechaInicio'] = str(fechaInicio)
        concurso['fechaFin'] = str(fechaFin)
        concurso['valorPagar'] = valorPagar
        concurso['url'] = url
        concurso['guion'] = guion
        concurso['recomendaciones'] = recomendaciones

        table_concurso.put_item(Item=concurso)

        return json.dump(concurso), 200
    else:
        return '', 204


@ app.route('/api/concurso/<string:url_c>', methods=['GET'])
def concursoConUrl(url_c):
    now = datetime.now()
    concurso = json.dumps(table_concurso.scan(FilterExpression=Attr(
        'url').eq(url_c) & Attr('fechaFin').gt(str(now)))['Items'][0])
    if not concurso:
        return jsonify({"msg": "No existe ningun concurso activo con la url especificada"}), 404
    return concurso, 200


@ app.route('/api/concurso/<string:url_c>/auth', methods=['GET'])
@ auth_required
def concursoConUrlAuth(url_c):
    user = current_user()
    now = datetime.now()
    concurso = json.dumps(table_concurso.scan(FilterExpression=Attr(
        'url').eq(url_c) & Attr('fechaFin').gt(str(now)))['Items'][0])
    if not concurso:
        return jsonify({"msg": "No existe ningun concurso activo con la url especificada"}), 404
    return concurso, 200


@ app.route('/api/voces/<string:id_c>', methods=['GET'])
def voces(id_c):
    try:
        voces = table_voz.scan(FilterExpression=Attr(
            'concursoId').eq(id_c))['Items']
        sorted(voces, key=sort_by_key)

        if not voces:
            return jsonify({"msg": "Este concurso aún no tiene voces de partcipantes"}), 404
        cantVoces = len(voces)
        return jsonify({"voces": voces, "pages": cantVoces/20}), 200
    except:
        return jsonify({"msg": "Este concurso aún no tiene voces de partcipantes"}), 404


@ app.route('/api/voces/<string:id_c>/auth', methods=['GET'])
@ auth_required
def vocesAuth(id_c):
    user = current_user()
    try:
        voces = table_voz.scan(FilterExpression=Attr(
            'concursoId').eq(id_c))['Items']
        sorted(voces, key=sort_by_key)

        if not voces:
            return jsonify({"msg": "Este concurso aún no tiene voces de partcipantes"}), 404
        cantVoces = len(voces)
        return jsonify({"voces": voces, "pages": cantVoces/20}), 200
    except:
        return jsonify({"msg": "Este concurso aún no tiene voces de partcipantes"}), 404


def sort_by_key(list):
    return list['fechaCreacion']


@ app.route('/api/audio/<string:id_v>', methods=['GET'])
def vocesArch(id_v):
    archivo = table_archivo_voz.get_item(Key={'id': id_v})['Item']

    return archivo['archivoConvertido'], 200


@ app.route('/api/convertido/<string:id_v>', methods=['GET'])
def vocesConv(id_v):
    archivo = table_archivo_voz.get_item(Key={'id': id_v})['Item']
    convertido = archivo['convertido']

    return jsonify({"convertido": convertido}), 200


@ app.route('/api/audio/<string:id_v>/auth', methods=['GET'])
@ auth_required
def vocesArchAuth(id_v):
    user = current_user()
    archivo = table_archivo_voz.get_item(Key={'id': id_v})['Item']
    return archivo['archivoOriginal'], 200


@ app.route('/api/audio/<string:id_v>/authB', methods=['GET'])
@ auth_required
def vocesArchAuthB(id_v):
    user = current_user()
    archivo = table_archivo_voz.get_item(Key={'id': id_v})['Item']

    convertido = archivo['convertido']

    return jsonify({"convertido": convertido}), 200


@ app.route('/api/audio/<string:id_v>/authC', methods=['GET'])
@ auth_required
def vocesArchAuthC(id_v):
    user = current_user()
    print(id_v)
    archivo = table_archivo_voz.get_item(Key={'id': id_v})['Item']

    return archivo['archivoConvertido'], 200


@ app.route('/api/audios3/<string:id>', methods=['GET'])
def get_audio_s3(id):
    audio = table_archivo_voz.get_item(Key={'id': id})['Item']
    if audio:
        return json.dumps(audio), 200
    else:
        return jsonify({"msg": "No se pudo encontrar el archivo solicitado"}), 404


@ app.route('/api/voz', methods=['POST'])
def subir_voz():
    fechaCreacion = datetime.now()
    req = json.loads(request.data)
    email = req.get('email', None)
    nombres = req.get('nombres', None)
    apellidos = req.get('apellidos', None)
    observaciones = req.get('observaciones', None)
    archivoId = req.get('archivoId', None)
    concursoId = req.get('concursoId', None)

    try:
        item = {
            'id': archivoId,
            'fechaCreacion': str(fechaCreacion),
            'email': email,
            'nombres': nombres,
            'apellidos': apellidos,
            'observaciones': observaciones,
            'archivoId': archivoId,
            'concursoId': concursoId,
        }
        table_voz.put_item(Item=item)

        return item, 201
    except:
        return 'Resource (Concurso or Archivo_Voz) not found.', 404


@ app.route('/api/audio', methods=['POST'])
def audio():
    if not 'file' in request.files:
        return jsonify({"msg": "La peticion debe tener un archivo"}), 404
    file = request.files['file']
    filen = file.filename
    ext = filen.split('.')[1].lower() if '.' in filen else ''
    if not ext in ALLOWED_EXTENSIONS:
        return jsonify({"msg": "La extensión no es válida"}), 404
    else:
        try:
            # upload files to s3
            filename = secure_filename(filen)
            archivo_voz_id = str(uuid.uuid4())
            s3.Bucket(
                'audios-supervoices').put_object(Key='audios/{}/{}'.format(archivo_voz_id, filename), Body=file)
            archivo_voz_ruta_original = 'https://audios-supervoices.s3.amazonaws.com/audios/{}/{}'.format(
                archivo_voz_id, filename)
            filename_converted = filename.split('.')[0]
            filename_converted += '.mp3'
            archivo_voz_ruta_convertido = 'https://audios-supervoices.s3.amazonaws.com/audios/{}/{}'.format(
                archivo_voz_id, filename_converted)

            item = {
                'id': archivo_voz_id,
                'archivoOriginal': archivo_voz_ruta_original,
                'archivoConvertido': archivo_voz_ruta_convertido,
                'convertido': False,
            }
            table_archivo_voz.put_item(Item=item)

            # post to sqs
            queue.send_message(
                MessageBody=archivo_voz_id,
                MessageDeduplicationId='archivo_voz',
                MessageGroupId='archivo_voz'
            )

            print(table_archivo_voz.get_item(
                Key={'id': archivo_voz_id})['Item'])

            return {"id": archivo_voz_id}, 201
        except:
            traceback.print_exc()
            return jsonify({"msg": "Error guardando el archivo"}), 500


if __name__ == '_main_':
    app.run(debug=True)
