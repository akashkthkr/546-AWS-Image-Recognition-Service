from quart import Quart, request, jsonify
from PIL import Image
from time import sleep
import base64
import asyncio
import boto3
import json
import constants
from SQSManagement import *
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'loggers': {
        'quart.app': {
            'level': 'DEBUG',
        },
    },
})
REQUEST_QUEUE_NAME = constants.AWS_SQS_REQUEST_QUEUE_NAME
RESPONSE_QUEUE_NAME = constants.AWS_SQS_RESPONSE_QUEUE_NAME

async def async_get_data(msg):
    sleep(1)
    return str(msg)

app = Quart(__name__)

@app.route('/classify-image', methods=['POST'])
async def classify_image():
    file = (await request.files)['myfile']
    key = str(file.filename)
    value = base64.b64encode(file.read())
    value = str(value, 'utf-8')

    # create message
    json_msg = json.dumps({'key': key, 'value': value})
    app.logger.debug("Request processed with payload %s", json_msg)

    # send message to SQS
    send_message(get_queue_url(), json_msg)

    # receive message from SQS
    return await async_get_data(json_msg)
  
@app.route('/health', methods=['GET'])
def healthcheck():
  app.logger.debug('OK')
  return "200"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=6060)