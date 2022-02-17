from email import message
import email
#from extensions import celery
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from celery import Celery
import ffmpeg
from utils.conn import db_session
from app import ArchivoVoz, Voz

app = Celery('tasks', broker='redis://localhost:6379/0')
emailFrom = 'noreplysupervoices@gmail.com'
emailFromPassword = 'sv123noreply!'

ip_front = 'localhost:5000'

class SqlAlchemyCloseHandlerTask(app.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()

def convertir_a_mp3(path_origen: str, path_destino: str,emailTo,nombres):
    dirname = os.getcwd()
    #print(f'dirname {dirname}')
    rel_origin = dirname + path_origen[1:].replace('/', '\\')
    rel_destino = dirname + path_destino[1:].replace('/', '\\')
    rel_origin = rel_origin.replace('\\', '/')
    rel_destino = rel_destino.replace('\\', '/')
    proc = subprocess.Popen(
        ['ffmpeg', '-nostdin', '-y', '-i', rel_origin, rel_destino])
    # print(proc)
    proc.wait()


    enviar_email(emailFrom, emailFromPassword,
            emailTo, nombres)
 
    


def enviar_email(emailFrom, emailFromPassword, emailTo, nombres):
    content = ''' Hola {}, esperamos que estes bien.

    Te informamos que tu voz ya ha sido procesada y publicada en la pagina del concurso.
    Si tu voz es elegida como ganadora, te contactaremos a traves de este medio.

    Un feliz dia.
    SuperVoices.'''.format(nombres)

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

def mapVoz(xy):
    x,y = xy
    return y

@app.task(base=SqlAlchemyCloseHandlerTask)
def process_audio_files():
    pending_voices = (
        db_session.query(Voz, ArchivoVoz)
        .filter(Voz.archivoId==ArchivoVoz.id)
        .filter(ArchivoVoz.convertido==False)
        .all()
    )

    if pending_voices:

        for (voz,archiVoz) in pending_voices:
            filename = archiVoz.archivoOriginal
            filename2 = archiVoz.archivoConvertido
            emailTo = voz.email
            nombresTo = voz.nombres
            
            try:
                convertir_a_mp3(filename,filename2,emailTo,nombresTo)
                archiVoz.convertido = True
            except Exception as e:
                print(e)

        converted_voices = list(
            filter(
                lambda xy: (mapVoz(xy).convertido == True),
                pending_voices,
            )
        )

        db_session.add_all(map(mapVoz, converted_voices))
        db_session.commit()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls process_audio_files every 1 minutes.
    sender.add_periodic_task(
        60, process_audio_files.s(), name="Process Files every 1 minutes"
    )
