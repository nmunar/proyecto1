# import enum
from enum import unique
from xmlrpc.client import DateTime
from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
from dateutil import parser
# from marshmallow_enum import EnumField
from flask_cors.extension import CORS
import json

POSTGRES = {
    'user': 'postgres',
    'pw': 'bd123',
    'db': 'concursos',
    'host': 'localhost',
    'port': '5432',
}


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nikitos99@localhost/concursos'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)

# Models


class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(220), nullable=0)
    apellidos = db.Column(db.String(220), nullable=0)
    email = db.Column(db.String(120), nullable=0, unique=1)
    contrasena = db.Column(db.String(300), nullable=0)
    # relaciones
    concursos = db.relationship('Concurso', backref='administrador', lazy=1)


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


# Schemas


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


# Concursos
@app.route('/api/<int:idAdmin>/concursos', methods=['GET', 'POST'])
def concursos(idAdmin):
    if request.method == 'GET':
        return schema_concursos.dumps(Concurso.query.all())
    elif request.method == 'POST':
        req = json.loads(request.data)
        nombre = req.get('nombre', None)
        imagen = req.get('imagen', None)
        url = req.get('url', None)
        fechaCreacion = datetime.now()
        fechaInicio = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        fechaFin = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        if(fechaInicio > fechaFin):
            return {"error": "La fecha de inicio es mayor a la de fin"}, 403
        valorPagar = req.get('valorPagar', None)
        guion = req.get('guion', None)
        recomendaciones = req.get('recomendaciones', None)
        administrador_id = idAdmin
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


@app.route('/api/<int:idAdmin>/concursos/<int:idConcurso>', methods=['GET', 'PUT', 'DELETE'])
def concurso(idAdmin, idConcurso):
    concurso = Concurso.query.get_or_404(idConcurso)
    if idAdmin != concurso.administrador_id:
        return {"msg": "Solo se tiene acceso a sus propios concursos"}, 403

    if request.method == 'GET':
        return schema_concurso.dump(concurso)
    elif request.method == 'PUT':
        req = json.loads(request.data)
        nombre = req.get('nombre', None)
        imagen = req.get('imagen', None)
        url = req.get('url', None)
        fechaInicio = parser.parse(req.get('fechaInicio', None), ignoretz=True)
        fechaFin = parser.parse(req.get('fechaFin', None), ignoretz=True)
        if(fechaInicio > fechaFin):
            return {"error": "La fecha de inicio es mayor a la de fin"}, 403
        valorPagar = req.get('valorPagar', None)
        guion = req.get('guion', None)
        recomendaciones = req.get('recomendaciones', None)
        concurso.nombre = nombre
        concurso.imagen = imagen
        concurso.url = url
        concurso.fechaInicio = fechaInicio
        concurso.fechaFin = fechaFin
        concurso.valorPagar = valorPagar
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
    print(url_c)
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
        return jsonify({"msg": "Este concurso aún no tiene voces de partcipantes"}), 404
    cantVoces = len(voces)
    return jsonify({"voces":schema_voz.dump(voces),"pages":cantVoces/20}), 200

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
        return send_file(archivo.archivoOriginal),200
    else:
        return send_file(archivo.archivoConvertido),200
    

if __name__ == '__main__':
    app.run(debug=True)
