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
import schedule
import time

dictConfig({
    'version': 1,
    
    'loggers': {
        'quart.app': {
            'level': 'DEBUG',
        },
    },
})

result_dict = {}

REQUEST_QUEUE_NAME = constants.AWS_SQS_REQUEST_QUEUE_NAME
RESPONSE_QUEUE_NAME = constants.AWS_SQS_RESPONSE_QUEUE_NAME

app = Quart(__name__)

def collect_response():
    queue_url = get_queue_url(constants.AWS_SQS_RESPONSE_QUEUE_NAME)
    response = receive_message(queue_url)
    app.logger.debug("Recevied response from queue %s", response)
    for message in response.get("Messages", []):
        message_body = message['Body']
        message_dict = json.loads(message_body)
        result_dict[message_dict['key']] = message_dict['value']
        delete_message(queue_url, message['ReceiptHandle'])

async def get_result(key):
    while True:
        sleep(1)
        if key in result_dict:
            return result_dict[key]
        
        
@app.route('/classify-image', methods=['POST'])
async def classify_image():
    file = (await request.files)['myfile']
    value = base64.b64encode(file.read())
    value = str(value, 'utf-8')
    key = str(file.filename)
    # create message
    json_msg = json.dumps({'key': key, 'value': value})
    # app.logger.debug("Request processed with payload %s", json_msg['key'])

    # send message to SQS
    send_message(get_queue_url(constants.AWS_SQS_REQUEST_QUEUE_NAME), json_msg)

    # receive message from SQS
    return await get_result(key)
  
@app.route('/health', methods=['GET'])
def healthcheck():
  app.logger.debug('OK')
  return "200"

if __name__ == '__main__':
    schedule.every(2).seconds.do(collect_response())
    app.logger.info(constants.STARTUP_BANNER)
    app.logger.info(constants.STARTUP_BANNER_GROUP)
    app.run(host='0.0.0.0', debug=True, port=6060)