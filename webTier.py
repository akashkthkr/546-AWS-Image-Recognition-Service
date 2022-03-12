from flask import Flask, render_template , request , jsonify
from PIL import Image
import os , io , sys
import numpy as np
import cv2
import base64
# from multiprocessing import Process

def run_task(key, value):
	# store key and value in S3

	# push the request in SQS queue

	# return the result to the user

app = Flask(__name__)

@app.route('/webTier' , methods=['POST'])
def webTier():
	file = request.files['myfile']
	key = file.filename
	value = base64.b64encode(file.read())
	# task_cb = Process(target=run_task, args=( key, value))
    # task_cb.start()
	return jsonify({'key':str(key), 'value': str(value)})

if __name__ == '__main__':
    # debug mode
    app.run(host='0.0.0.0', debug=True, port=6060)
