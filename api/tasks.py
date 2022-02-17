from email import message
import email
from celery import Celery
from app import ArchivoVoz, Concurso, Administrador, db
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import ffmpeg
from celery.utils.log import get_task_logger
import flask_praetorian
from flask_praetorian import auth_required, current_user

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/0')
guard = flask_praetorian.Praetorian()
emailFrom = 'noreplysupervoices@gmail.com'
emailFromPassword = 'sv123noreply!'

ip_front = 'localhost:5000'


@app.task
def convertir_a_mp3(archivo_id, path_origen: str, path_destino: str):
    dirname = os.getcwd()
    #print(f'dirname {dirname}')
    rel_origin = dirname + path_origen[1:].replace('/', '\\')
    rel_destino = dirname + path_destino[1:].replace('/', '\\')

    # print(rel_origin)
    # print(rel_destino)
    proc = subprocess.Popen(
        ['ffmpeg', '-nostdin', '-y', '-i', rel_origin, rel_destino])
    # print(proc)
    proc.wait()
    archivo = ArchivoVoz.query.get(int(archivo_id))
    archivo.convertido = True
    db.session.commit()
    voz = archivo.voz
    print(voz.email)
    emailTo = voz.email
    nombres = voz.nombres
    concurso = Concurso.query.get(int(voz.concursoId))
    concursoURL = concurso.url
    urlConcursoFull = 'http://127.0.0.1:3000/home/concurso/{}'.format(
        concursoURL)
    admin = Administrador.query.get(concurso.administrador_id)
    print(admin.email)
    print()
    enviar_email(emailFrom, emailFromPassword,
                 emailTo, nombres, urlConcursoFull)


def enviar_email(emailFrom, emailFromPassword, emailTo, nombres, urlConcursoFull):
    content = ''' Hola {}, esperamos que estes bien.

    Te informamos que tu voz ya ha sido procesada y publicada en la pagina del concurso. Puedes consultar en el siguiente enlace:
    {}
    Si tu voz es elegida como ganadora, te contactaremos a traves de este medio.

    Un feliz dia.
    SuperVoices.'''.format(nombres, urlConcursoFull)
    message = MIMEMultipart()
    message['From'] = emailFrom
    message['To'] = emailTo
    message['Subject'] = 'Procesamiento de voz exitoso - SuperVoices'
    message.attach(MIMEText(content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(emailFrom, emailFromPassword)
    text = message.as_string()
    session.sendmail(emailFrom, emailTo, text)
    session.quit()
