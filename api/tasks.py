import subprocess
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery import Celery
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import os
import json
from types import SimpleNamespace
from pydub import AudioSegment
import requests
from dotenv import load_dotenv

load_dotenv()

app = Celery('tasks', broker='redis://localhost:6379/0')
emailFrom = 'noreplysupervoices@gmail.com'
emailFromPassword = 'sv123noreply!'

ip_front = 'localhost:5000'

my_config = Config(
    region_name='us-east-1',
)

s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.environ.get('AWS_ACCSESS_KEY_ID_DYNAMO'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCSESS_KEY_DYNAMO'),
                          aws_session_token=os.environ.get('AWS_SESSION_TOKEN_DYNAMO'), region_name=os.environ.get('REGION_NAME_DYNAMO'))
sqs = boto3.client('sqs', region_name=os.environ.get('REGION_NAME_SQS'), aws_access_key_id=os.environ.get('AWS_ACCSESS_KEY_ID_SQS'),
                   aws_secret_access_key=os.environ.get('AWS_SECRET_ACCSESS_KEY_SQS'), aws_session_token=os.environ.get('AWS_SESSION_TOKEN_SQS'))

table_archivo_voz = dynamodb.Table('archivo_voz')
table_voz = dynamodb.Table('voz')

QUEUE_URL = str(os.environ.get('SQS_QUEUE_URL'))


class SqlAlchemyCloseHandlerTask(app.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


def convertir_a_mp3(path_origen: str, path_destino: str, emailTo, nombres, id: str):

    # proc = subprocess.Popen(['ffmpeg', '-nostdin', '-y', '-i', path_origen, path_destino],
    #                         stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    # proc.wait()

    archivo_original = requests.get(path_origen, allow_redirects=True)
    file_name_to_s3 = ''
    if path_destino.find('/'):
        file_name_to_s3 = path_destino.rsplit('/', 1)[1]
    open('/audiosOriginales/{}'.format(id),
         'wb').write(archivo_original.content)

    AudioSegment.from_file('/audiosOriginales/{}'.format(id)
                           ).export("/audiosConvertidos/{}".format(file_name_to_s3), format="mp3")

    with open('/audiosConvertidos/{}'.format(file_name_to_s3), 'r') as file:
        data = file.read().replace('\n', '')
        s3.Bucket(
            'audios-supervoices').put_object(Key='audios/{}/{}'.format(id, file_name_to_s3), Body=file)

    # enviar_email(emailFrom, emailFromPassword,
    #              emailTo, nombres)


def enviar_email(emailFrom, emailFromPassword, emailTo, nombres):
    mensaje = Mail(
        from_email=emailFrom,
        to_emails=emailTo,
        subject='Procesamiento de voz exitoso - SuperVoices')

    mensaje.dynamic_template_data = {'nombres': nombres}

    mensaje.template_id = ''

    try:
        sg = SendGridAPIClient('')
        response = sg.send(mensaje)
    except Exception as e:
        print(e)


def mapVoz(xy):
    x, y = xy
    return y


@app.task(base=SqlAlchemyCloseHandlerTask)
def process_audio_files():

    mensajesPorIteracion = 3

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=mensajesPorIteracion,
        MessageAttributeNames=[
            'All'
        ],
        WaitTimeSeconds=0
    )

    i = 0

    pending_voices = []

    while i < len(response['Messages']):
        message = response['Messages'][i]

        archivo_voz_json = table_archivo_voz.get_item(
            Key={'id': message['Body']})['Item']
        voz_json = table_voz.get_item(Key={'id': message['Body']})['Item']
        archivo_voz_object = json.loads(
            archivo_voz_json, object_hook=lambda d: SimpleNamespace(**d))
        voz_object = json.loads(
            voz_json, object_hook=lambda d: SimpleNamespace(**d))
        print(voz_object)
        print(voz_object.id)

        tuple_voz_archivo = (voz_object, archivo_voz_object)
        print(tuple_voz_archivo)
        pending_voices.append(tuple_voz_archivo)

        receipt_handle = message['ReceiptHandle']

        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
        i += 1

    if pending_voices:
        for (voz, archiVoz) in pending_voices:
            try:
                convertir_a_mp3(archiVoz.archivoOriginal,
                                archiVoz.archivoOriginal, voz.email, voz.nombres, voz.id)
                item = {
                    'id': archiVoz.id,
                    'archivoOriginal': archiVoz.archivoOriginal,
                    'archivoConvertido': archiVoz.archivoConvertido,
                    'convertido': True
                }
                table_archivo_voz.put_item(Item=item)
            except Exception as e:
                print(e)

        # converted_voices = list(
        #     filter(
        #         lambda xy: (mapVoz(xy).convertido == True),
        #         pending_voices,
        #     )
        # )

        # set attribute convertido to True (Dyanamo)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls process_audio_files every 1 minutes.
    sender.add_periodic_task(
        60, process_audio_files.s(), name="Process Files every 1 minutes"
    )
