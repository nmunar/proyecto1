import subprocess
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery import Celery
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

    proc = subprocess.Popen(['ffmpeg', '-nostdin', '-y', '-i', path_origen, path_destino],stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.wait()

    enviar_email(emailFrom, emailFromPassword,
            emailTo, nombres)
 
    


def enviar_email(emailFrom, emailFromPassword, emailTo, nombres):
    mensaje = Mail(
       from_email = emailFrom,
        to_emails = emailTo,
        subject='Procesamiento de voz exitoso - SuperVoices')
    
    mensaje.dynamic_template_data = {'nombres': nombres}

    mensaje.template_id = ''

    try:
        sg = SendGridAPIClient('')
        response = sg.send(mensaje)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


    
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
