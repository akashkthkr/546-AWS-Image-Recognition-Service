from quart import Quart, request, jsonify
from PIL import Image
# import time
from time import sleep
import base64
import asyncio
#import boto3
#from SQSManagement import *


async def async_get_data(msg):
    sleep(1)
    return str(msg)

app = Quart(__name__)

@app.route('/webTier' , methods=['POST'])
async def webTier():
	file = (await request.files)['myfile']
	key = str(file.filename)
	value = base64.b64encode(file.read())
	value = str(value, 'utf-8')
	msg = {'key': key, 'value': value}
	return await async_get_data(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=6060)
