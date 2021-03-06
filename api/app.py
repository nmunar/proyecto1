from enum import unique
import os
from xmlrpc.client import DateTime
from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
from dateutil import parser
from werkzeug.utils import secure_filename
import flask_praetorian
from marshmallow_enum import EnumField
from flask_cors.extension import CORS
import json
import traceback
from flask_praetorian import auth_required, current_user

POSTGRES = {
    'user': 'postgres',
    'pw': 'admin',
    'db': 'concursos',
    'host': 'localhost',
    'port': '5432',
}


dirname = os.getcwd()
dirname = dirname.replace('\\proyecto1\\api', '\\efs').replace('\\', '/')
UPLOAD_FOLDER = dirname+'/audiosOriginales/'

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'aac', 'ogg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a random string'
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nikitos99@concursos.cdqova1igbuq.us-east-1.rds.amazonaws.com/concursos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERT_FOLDER'] = dirname+'/audiosConvertidos/'
app.config['BROKER_URL'] = 'redis://localhost:6379/0'

CORS(app)
guard = flask_praetorian.Praetorian()

db = SQLAlchemy(app)

ma = Marshmallow(app)
#api = Api(app)

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
    concursos = db.relationship('Concurso', backref='administrador', lazy=1)

    @property
    def rolenames(self):
        return []

    @property
    def password(self):
        return self.contrasena

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return True


class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=0)
    imagen = db.Column(db.String(200), nullable=1)
    url = db.Column(db.String(120), nullable=0, unique=1)
    fechaCreacion = db.Column(db.DateTime)
    fechaInicio = db.Column(db.DateTime, nullable=0)
    fechaFin = db.Column(db.DateTime, nullable=0)
    valorPagar = db.Column(db.Integer, nullable=0)
    guion = db.Column(db.String(3000), nullable=0)
    recomendaciones = db.Column(db.String(2000), nullable=0)
    # relaciones
    administrador_id = db.Column(
        db.Integer, db.ForeignKey('administrador.id'), nullable=0)
    voces = db.relationship('Voz', backref='concurso',
                            cascade="all, delete", lazy=1)

# Voz


class Voz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fechaCreacion = db.Column(db.DateTime, nullable=0)
    email = db.Column(db.String(120), nullable=0)
    nombres = db.Column(db.String(220), nullable=0)
    apellidos = db.Column(db.String(220), nullable=0)
    observaciones = db.Column(db.String(1000))
    # relaciones
    concursoId = db.Column(
        db.Integer, db.ForeignKey('concurso.id'), nullable=0)
    archivoId = db.Column(db.Integer, db.ForeignKey(
        'archivoVoz.id'), nullable=0)


class ArchivoVoz(db.Model):
    __tablename__ = 'archivoVoz'
    id = db.Column(db.Integer, primary_key=True)
    archivoOriginal = db.Column(db.String(120), nullable=1)
    archivoConvertido = db.Column(db.String(120), nullable=1)
    convertido = db.Column(db.Boolean, nullable=0, default=0)
    # relaciones
    voz = db.relationship('Voz', backref=db.backref(
        'archivoVoz', cascade="all, delete"), uselist=False, lazy=1)


# --------------------------- Schemas ---------------------------


class Administrador_Schema(ma.Schema):
    class Meta:
        fields = ("id", "nombres", "apellidos", "email")


schema_administrador = Administrador_Schema()
schema_administradores = Administrador_Schema(many=True)


class Concurso_Schema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "imagen", "url", "fechaCreacion",
                  "fechaInicio", "fechaFin", "valorPagar", "guion", "recomendaciones")


schema_concurso = Concurso_Schema()
schema_concursos = Concurso_Schema(many=True)


class ArchivoVozSchema(ma.Schema):
    class Meta:
        fields = ("id", "convertido", "archivoOriginal", "archivoConvertido")


schema_archivoVoz = ArchivoVozSchema()
schema_archivosVoz = ArchivoVozSchema(many=1)


class Voz_Schema(ma.Schema):
    class Meta:
        fields = ("id", "fechaCreacion", "email", "nombres", "apellidos",
                  "convertida", "observaciones", "concursoId", "archivoId")


class Voz_SchemaSeguro(ma.Schema):
    class Meta:
        fields = ("fechaCreacion", "archivoId")


schema_voz = Voz_Schema()
schema_voces = Voz_Schema(many=1)
schemaSeguro_voz = Voz_SchemaSeguro(many=1)


# --------------------------- Routes ---------------------------

guard.init_app(app, Administrador)

# userAdmin


@app.route('/api/login', methods=['POST'])
def login():
    req = json.loads(request.data)
    email = req.get('email', None)
    contrasena = req.get('contrasena', None)
    admin = guard.authenticate(email, contrasena)
    return jsonify({'access_token': guard.encode_jwt_token(admin)}), 200


@app.route('/api/register', methods=['POST'])
def register():
    req = json.loads(request.data)
    nombres = req.get('nombres', None)
    apellidos = req.get('apellidos', None)
    email = req.get('email', None)
    contrasena = req.get('contrasena', None)
    if db.session.query(Administrador).filter_by(email=email).count() == 0:
        db.session.add(Administrador(
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            contrasena=guard.hash_password(contrasena)
        ))
        db.session.commit()
        return {"msg": "Usuario creado"}, 201

    else:
        return {"msg": "Correo ya registrado"}, 400

# Concursos


@app.route('/api/concursos', methods=['GET', 'POST'])
@auth_required
def concursos():
    user = current_user()
    if request.method == 'GET':
        return schema_concursos.dumps(user.concursos)
    elif request.method == 'POST':
        req = json.loads(request.data)
        nombre = req.get('nombre', None)
        imagen = req.get('imagen', None)
        url = req.get('url', None)
        concursoURL = Concurso.query.filter_by(url=req.get('url')).first()
        if concursoURL:
            return {"error": "La URL del concurso ya se usa"}, 403
        fechaCreacion = datetime.now()
        fechaInicio = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        fechaFin = parser.parse(req.get('fechaFin', None), ignoretz=True)
        if(fechaInicio > fechaFin):
            return {"error": "La fecha de inicio es mayor a la de fin"}, 403
        valorPagar = req.get('valorPagar', None)
        guion = req.get('guion', None)
        recomendaciones = req.get('recomendaciones', None)
        administrador_id = user.id
        concurso = Concurso(
            nombre=nombre,
            imagen=imagen,
            url=url,
            fechaCreacion=fechaCreacion,
            fechaInicio=fechaInicio,
            fechaFin=fechaFin,
            valorPagar=valorPagar,
            guion=guion,
            recomendaciones=recomendaciones,
            administrador_id=administrador_id
        )
        db.session.add(concurso)
        db.session.commit()
        return {"id": concurso.id, "fechaCreacion": str(concurso.fechaCreacion)}, 201


@app.route('/api/concursos/<int:idConcurso>', methods=['GET', 'PUT', 'DELETE'])
@auth_required
def concurso(idConcurso):
    user = current_user()
    concurso = Concurso.query.get_or_404(idConcurso)
    if user.id != concurso.administrador_id:
        return {"msg": "Solo se tiene acceso a sus propios concursos"}, 403

    if request.method == 'GET':
        return schema_concurso.dump(concurso)
    elif request.method == 'PUT':
        req = json.loads(request.data)
        nombre = req.get('nombre', None)
        imagen = req.get('imagen', None)
        fechaInicio = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        fechaFin = parser.parse(req.get('fechaFin', None), ignoretz=True)
        if(fechaInicio > fechaFin):
            return {"error": "La fecha de inicio es mayor a la de fin"}, 403
        valorPagar = req.get('valorPagar', None)
        concursoURL = Concurso.query.filter_by(url=req.get('url')).first()
        if concursoURL and concursoURL.id != idConcurso:
            return {"error": "La URL del concurso ya se usa"}, 403
        url = req.get('url', None)
        guion = req.get('guion', None)
        recomendaciones = req.get('recomendaciones', None)
        concurso.nombre = nombre
        concurso.imagen = imagen
        concurso.fechaInicio = fechaInicio
        concurso.fechaFin = fechaFin
        concurso.valorPagar = valorPagar
        concurso.url = url
        concurso.guion = guion
        concurso.recomendaciones = recomendaciones
        db.session.commit()
        return schema_concurso.dump(concurso), 200
    else:
        db.session.delete(concurso)
        db.session.commit()
        return '', 204


@app.route('/api/concurso/<string:url_c>', methods=['GET'])
def concursoConUrl(url_c):
    now = datetime.now()
    concurso = Concurso.query.filter_by(
        url=url_c).filter(Concurso.fechaFin > now).first()
    if not concurso:
        return jsonify({"msg": "No existe ningun concurso activo con la url especificada"}), 404
    return schema_concurso.dump(concurso), 200


@app.route('/api/voces/<string:id_c>', methods=['GET'])
def voces(id_c):
    voces = Voz.query.filter_by(
        concursoId=id_c).order_by(Voz.fechaCreacion.desc()).all()

    if not voces:
        return jsonify({"msg": "Este concurso a??n no tiene voces de partcipantes"}), 404
    cantVoces = len(voces)
    return jsonify({"voces": schema_voces.dump(voces), "pages": cantVoces/20}), 200


@app.route('/api/audio/<string:id_v>', methods=['GET'])
def vocesArch(id_v):
    archivo = ArchivoVoz.query.get_or_404(id_v)
    voz = archivo.voz

    convertido = request.args.get('convertido') == '1'

    if not voz or not archivo.voz:
        return jsonify({"msg": "No se pudo encontrar el archivo solicitado"}), 404
    if(convertido and not archivo.convertido):
        return jsonify({"msg": "el archivo no se ha convertido"}), 404
    elif (not convertido and not archivo.convertido):
        return send_file(archivo.archivoOriginal), 200
    else:
        return send_file(archivo.archivoConvertido), 200


@app.route('/api/audio', methods=['POST'])
def audio():
    print(request.files)
    if not 'file' in request.files:
        return jsonify({"msg": "La peticion debe tener un archivo"}), 404
    file = request.files['file']
    filen = file.filename
    ext = filen.split('.')[1].lower() if '.' in filen else ''
    if not ext in ALLOWED_EXTENSIONS:
        return jsonify({"msg": "La extensi??n no es v??lida"}), 404
    else:
        filename = secure_filename(filen)
        archivo_voz = ArchivoVoz()
        db.session.add(archivo_voz)
        db.session.commit()
    try:
        upload_directory = os.path.join(
            app.config['UPLOAD_FOLDER'], '{}/'.format(archivo_voz.id))
        convert_directory = os.path.join(
            app.config['CONVERT_FOLDER'], '{}/'.format(archivo_voz.id))
        os.makedirs(upload_directory, exist_ok=True)
        os.makedirs(convert_directory, exist_ok=True)
        path = os.path.join(upload_directory, filename)
        convert_path = os.path.join(
            convert_directory, '{}.mp3'.format(os.path.splitext(filename)[0]))
        archivo_voz.archivoOriginal = path
        archivo_voz.archivoConvertido = convert_path
        file.save(path)
        db.session.commit()
        return schema_archivoVoz.dump(archivo_voz), 201
    except:
        traceback.print_exc()
        db.session.delete(archivo_voz)
        db.session.commit()
        return jsonify({"msg": "Error guardando el archivo"}), 500


@app.route('/api/voz', methods=['POST'])
def subir_voz():
    fechaCreacion = datetime.now()
    req = json.loads(request.data)
    email = req.get('email', None)
    nombres = req.get('nombres', None)
    apellidos = req.get('apellidos', None)
    observaciones = req.get('observaciones', None)
    archivoId = req.get('archivoId', None)
    concursoId = req.get('concursoId', None)

    Concurso.query.get_or_404(concursoId)
    archivo = ArchivoVoz.query.get_or_404(archivoId)
    if not archivo.archivoOriginal:
        return jsonify({"msg": "Archivo de audio no existente"}), 404

    voz = Voz(
        fechaCreacion=fechaCreacion,
        email=email,
        nombres=nombres,
        apellidos=apellidos,
        observaciones=observaciones,
        archivoId=archivoId,
        concursoId=concursoId,
    )
    db.session.add(voz)
    db.session.commit()
    return schema_voz.dump(voz), 201


@app.route('/api/concurso/<string:url_c>/auth', methods=['GET'])
@auth_required
def concursoConUrlAuth(url_c):
    user = current_user()
    now = datetime.now()
    concurso = Concurso.query.filter_by(
        url=url_c).filter(Concurso.fechaFin > now).first()
    if not concurso:
        return jsonify({"msg": "No existe ningun concurso activo con la url especificada"}), 404
    return schema_concurso.dump(concurso), 200


@app.route('/api/voces/<string:id_c>/auth', methods=['GET'])
@auth_required
def vocesAuth(id_c):
    user = current_user()
    voces = Voz.query.filter_by(
        concursoId=id_c).order_by(Voz.fechaCreacion.desc()).all()

    if not voces:
        return jsonify({"msg": "Este concurso a??n no tiene voces de partcipantes"}), 404
    cantVoces = len(voces)
    return jsonify({"voces": schema_voces.dump(voces), "pages": cantVoces/20}), 200


@app.route('/api/audio/<string:id_v>/auth', methods=['GET'])
@auth_required
def vocesArchAuth(id_v):
    user = current_user()
    archivo = ArchivoVoz.query.get_or_404(id_v)
    voz = archivo.voz

    convertido = archivo.convertido

    if not voz or not archivo.voz:
        return jsonify({"msg": "No se pudo encontrar el archivo solicitado"}), 404
    else:
        return send_file(archivo.archivoOriginal), 200


@app.route('/api/audio/<string:id_v>/authC', methods=['GET'])
@auth_required
def vocesArchAuthC(id_v):
    user = current_user()
    archivo = ArchivoVoz.query.get_or_404(id_v)
    voz = archivo.voz

    convertido = archivo.convertido

    if not voz or not archivo.voz:
        return jsonify({"msg": "No se pudo encontrar el archivo solicitado"}), 404
    if(convertido and not archivo.convertido):
        return jsonify({"msg": "el archivo no se ha convertido"}), 404
    elif (not convertido and not archivo.convertido):
        return jsonify({"msg": "el archivo no se ha convertido aun"}), 204
    else:
        return send_file(archivo.archivoConvertido), 200


@app.route('/api/audio/<string:id_v>/authB', methods=['GET'])
@auth_required
def vocesArchAuthB(id_v):
    user = current_user()
    archivo = ArchivoVoz.query.get_or_404(id_v)
    voz = archivo.voz

    convertido = archivo.convertido

    if not voz or not archivo.voz:
        return jsonify({"msg": "No se pudo encontrar el archivo solicitado"}), 404
    else:
        return jsonify({"convertido": convertido}), 200


@app.route('/api/convertido/<string:id_v>', methods=['GET'])
def vocesConv(id_v):
    archivo = ArchivoVoz.query.get_or_404(id_v)
    voz = archivo.voz

    convertido = archivo.convertido

    if not voz or not archivo.voz:
        return jsonify({"msg": "No se pudo encontrar el archivo solicitado"}), 404
    else:
        return jsonify({"convertido": convertido}), 200

if __name__ == '_main_':
    app.run(debug=True)
