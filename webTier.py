from quart import Quart, request, jsonify
from PIL import Image
# import time
from time import sleep
import base64
import asyncio
import boto3
import constants
from SQSManagement import *

REQUEST_QUEUE_NAME = constants.AWS_SQS_REQUEST_QUEUE_NAME
RESPONSE_QUEUE_NAME = constants.AWS_SQS_RESPONSE_QUEUE_NAME


async def async_get_data(msg):
    sleep(1)
    return str(msg)


app = Quart(__name__)


@app.route('/webTier', methods=['POST'])
async def webTier():
    file = (await request.files)['myfile']
    key = str(file.filename)
    value = base64.b64encode(file.read())
    value = str(value, 'utf-8')

    # create message
    msg = {'key': key, 'value': value}
    json_msg = jsonify(msg)

    # send message to SQS
    queueUrl = get_queue_url(queue_name=REQUEST_QUEUE_NAME)
    send_message(queueUrl, json_msg)

    # receive message from SQS
    return await async_get_data(json_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=6060)
