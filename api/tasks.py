from celery import Celery
from app import ArchivoVoz, db
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import ffmpeg
app = Celery( 'tasks' , broker = 'redis://localhost:6379/0' )

ip_front = 'localhost:5000'

@app.task
def convertir_a_mp3(archivo_id, path_origen: str, path_destino: str):
    dirname = os.getcwd()
    print(f'dirname {dirname}')
    rel_origin = dirname + path_origen[1:].replace('/', '\\')
    rel_destino = dirname + path_destino[1:].replace('/', '\\')

    print(rel_origin)
    print(rel_destino)
    proc = subprocess.Popen(['ffmpeg', '-nostdin', '-y', '-i', rel_origin, rel_destino])
    print(proc)
    proc.wait()
    archivo = ArchivoVoz.query.get(int(archivo_id))
    archivo.convertido = True
    db.session.commit()

    #voz = archivo.voz
    #email_to = voz.email
    #nombres = voz.nombres
    #full_url = 'http://{}/{}'.format(ip_front, voz.concurso.url)
    #enviar_email(email_from, email_to, password, nombres, full_url)