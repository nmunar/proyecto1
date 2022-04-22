from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery import Celery
from utils.conn import db_session
import boto3
import os
from dotenv import load_dotenv
import json
from types import SimpleNamespace
from pydub import AudioSegment
import requests
import glob

load_dotenv()

app = Celery('tasks', broker='redis://localhost:6379/0')
emailFrom = 'noreplysupervoices@gmail.com'
emailFromPassword = 'sv123noreply!'

ip_front = 'localhost:5000'


s3 = boto3.resource('s3', region_name=os.environ.get('REGION_NAME_S3'),
                    aws_access_key_id=os.environ.get(
    'AWS_ACCSESS_KEY_ID_S3'),
    aws_secret_access_key=os.environ.get(
    'AWS_SECRET_ACCSESS_KEY_S3'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN_S3'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION_NAME_DYNAMO'),
                          aws_access_key_id=os.environ.get(
    'AWS_ACCSESS_KEY_ID_DYNAMO'),
    aws_secret_access_key=os.environ.get(
    'AWS_SECRET_ACCSESS_KEY_DYNAMO'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN_DYNAMO'))
sqs = boto3.client('sqs', region_name=os.environ.get('REGION_NAME_SQS'),
                   aws_access_key_id=os.environ.get(
    'AWS_ACCSESS_KEY_ID_SQS'),
    aws_secret_access_key=os.environ.get(
    'AWS_SECRET_ACCSESS_KEY_SQS'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN_SQS'))

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
    archivo_original = requests.get(path_origen, allow_redirects=True)
    file_name_to_s3 = ''
    extension = ''
    if path_destino.find('/'):
        file_name_to_s3 = path_destino.rsplit('/', 1)[1]
        extension = str(path_destino.rsplit('/', 1)[1]).split('.')[1]

    with open('./audiosOriginales/{}.{}'.format(id, extension), 'wb') as f:
        f.write(archivo_original.content)

    AudioSegment.from_file('./audiosOriginales/{}.{}'.format(id, extension)
                           ).export("./audiosConvertidos/{}".format(file_name_to_s3), format="mp3")

    with open('./audiosConvertidos/{}'.format(file_name_to_s3), 'rb') as f:
        contents = f.read()
        s3.Bucket(
            'audios-supervoices').put_object(Key='audios/{}/{}'.format(id, file_name_to_s3), Body=contents)
        os.remove('./audiosOriginales/{}.{}'.format(id, extension))

    #enviar_email(emailFrom, emailFromPassword, emailTo, nombres)


def enviar_email(emailFrom, emailFromPassword, emailTo, nombres):
    mensaje = Mail(
        from_email=emailFrom,
        to_emails=emailTo,
        subject='Procesamiento de voz exitoso - SuperVoices')

    mensaje.dynamic_template_data = {'nombres': nombres}
    mensaje.template_id = os.environ.get('TEMPLATE_ID_SENDGRID')
    try:
        sg = SendGridAPIClient(os.environ.get('API_CLIENT_SENDGRID'))
        sg.send(mensaje)
    except Exception as e:
        print(e)


def mapVoz(xy):
    x, y = xy
    return y


@app.task()
def process_audio_files():

    os.makedirs('./audiosOriginales', exist_ok=True)
    os.makedirs('./audiosConvertidos', exist_ok=True)

    mensajesPorIteracion = 3

    pending_voices = []
    try:
        response = sqs.receive_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/398814904431/supervoices.fifo',
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

        while i < len(response['Messages']):
            message = response['Messages'][i]
            receipt_handle = message['ReceiptHandle']

            sqs.delete_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/398814904431/supervoices.fifo',
                ReceiptHandle=receipt_handle
            )
            
            archivo_voz_json = table_archivo_voz.get_item(
                Key={'id': message['Body']})['Item']
            voz_json = table_voz.get_item(Key={'id': message['Body']})['Item']
            archivo_voz_object = json.loads(
                json.dumps(archivo_voz_json), object_hook=lambda d: SimpleNamespace(**d))
            voz_object = json.loads(
                json.dumps(voz_json), object_hook=lambda d: SimpleNamespace(**d))
            tuple_voz_archivo = (voz_object, archivo_voz_object)
            pending_voices.append(tuple_voz_archivo)
            i += 1
    except:
        print('SQS: no messages')

    if pending_voices:
        for (voz, archiVoz) in pending_voices:
            try:
                convertir_a_mp3(archiVoz.archivoOriginal,
                                archiVoz.archivoConvertido, voz.email, voz.nombres, voz.id)
                item = {
                    'id': archiVoz.id,
                    'archivoOriginal': archiVoz.archivoOriginal,
                    'archivoConvertido': archiVoz.archivoConvertido,
                    'convertido': True
                }
                table_archivo_voz.put_item(Item=item)
            except Exception as e:
                print(e)
        files = glob.glob('./audiosConvertidos/*')
        for f in files:
            os.remove(f)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls process_audio_files every 1 minutes.
    sender.add_periodic_task(
        15, process_audio_files.s(), name="Process Files every 15 secs"
    )
