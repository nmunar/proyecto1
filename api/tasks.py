import subprocess
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery import Celery
from utils.conn import db_session
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import os
import json
from types import SimpleNamespace
from pydub import AudioSegment
import requests

app = Celery('tasks', broker='redis://localhost:6379/0')
emailFrom = 'noreplysupervoices@gmail.com'
emailFromPassword = 'sv123noreply!'

ip_front = 'localhost:5000'

my_config = Config(
    region_name='us-east-1',
)
print(os.environ.get('REGION_NAME_SQS'), os.environ.get('AWS_ACCSESS_KEY_ID_SQS'),
      os.environ.get('AWS_SECRET_ACCSESS_KEY_SQS'), os.environ.get('AWS_SESSION_TOKEN_SQS'))
s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
dynamodb = boto3.resource('dynamodb', aws_access_key_id='ASIA3MN2XW6QJPJCMPWX', aws_secret_access_key='2zNJcLJx5D77gq3z1RRj+y0Lx6ZnNzD7CDd0lolN',
                          aws_session_token='FwoGZXIvYXdzEBcaDA7JTbdNqcSFQEjITSLHAZ4W2EDK3M9KP6rybpzAJgMse/ySTWc2ctF6oKQuR8w8G4R6XyagGD4uvi8US25CG4gVrav0AuhWAd6tbPM8aOL/voO3zFP+VqAyzhzkVBGUX0wfFzqoU1RDpl+DhqCLPxO640JnqH+seeN8KI0U7iOpFQklDCz568x3ugN2EG0q6zByMynD4J+J1+wGv67zl/PZZ5hvZicptSFQyUUCsoYJrKAOlfkXK/gZ0SH36BucwHKp+qYhErCc2nbUewss41VB5zAJvx8o4efskgYyLZEGMDoBxvs3WdzEfx+2FOvvNtICkg23M8GL5Y07C2ATVdWNgrcp/nExL5rc7Q==', region_name='us-east-1')
# sqs = boto3.client('sqs', region_name=os.environ.get('REGION_NAME_SQS'),
#                    aws_access_key_id=os.environ.get(
#     'AWS_ACCSESS_KEY_ID_SQS'),
#     aws_secret_access_key=os.environ.get(
#     'AWS_SECRET_ACCSESS_KEY_SQS'),
#     aws_session_token=os.environ.get('AWS_SESSION_TOKEN_SQS'))
sqs = boto3.client('sqs', region_name='us-east-1',
                   aws_access_key_id="ASIAVZWZYQBX2ZGI5L5F",
                   aws_secret_access_key="gyBQAa7T0wbDqVzk9Jtxm3SZEmseOV3qfgfT/XJE",
                   aws_session_token="FwoGZXIvYXdzEBYaDD1ws7CB0yO5uCewVSLJASNI2vSCV2s1n9W5zveud/nuKsBSVUnB957PDQAEC9ISoiT9mLyH6/F9FFUi2OoErP7Ud0SANNObuBUBs2oK5yESrQsR0sGlE3q9g8xgfxpI7Vr/NxP5vl31BfFurq97EY3gyuljex7Xqd4rJWZBe3rlBj1tomkhIDF9oXWTZzPMoH9b8x29TIQohoE/oaQAB6I7c42L8CmCfuTuFgeJdBoCCFqHZHMWa5knTkybrIktwGJb+baBPBhglmfp2LIfdf6Oo/YUGm/YKyjd0eySBjItR+eS1lqTnnz8+aVCOo7D+v9tlcJV3Xlji62XFkwTTwtsZ0alvW7t8jCvkqFW")

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
    print(path_origen)
    archivo_original = requests.get(path_origen, allow_redirects=True)
    file_name_to_s3 = ''
    extension = ''
    if path_destino.find('/'):
        file_name_to_s3 = path_destino.rsplit('/', 1)[1]
        extension = str(path_destino.rsplit('/', 1)[1]).split('.')[1]
        print(file_name_to_s3)
        print(extension)
    with open('./audiosOriginales/{}.{}'.format(id, extension), 'wb') as f:
        f.write(archivo_original.content)

    AudioSegment.from_file('./audiosOriginales/{}'.format(id)
                           ).export("./audiosConvertidos/{}".format(file_name_to_s3), format="mp3")

    with open('./audiosConvertidos/{}'.format(file_name_to_s3), 'r') as file:
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
            archivo_voz_json = table_archivo_voz.get_item(
                Key={'id': message['Body']})['Item']
            voz_json = table_voz.get_item(Key={'id': message['Body']})['Item']
            archivo_voz_object = json.loads(
                json.dumps(archivo_voz_json), object_hook=lambda d: SimpleNamespace(**d))
            voz_object = json.loads(
                json.dumps(voz_json), object_hook=lambda d: SimpleNamespace(**d))
            tuple_voz_archivo = (voz_object, archivo_voz_object)
            pending_voices.append(tuple_voz_archivo)

            receipt_handle = message['ReceiptHandle']

            sqs.delete_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/398814904431/supervoices.fifo',
                ReceiptHandle=receipt_handle
            )
            i += 1
    except:
        print('error SQS no messages')

    if pending_voices:
        for (voz, archiVoz) in pending_voices:
            print(voz.id)
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
