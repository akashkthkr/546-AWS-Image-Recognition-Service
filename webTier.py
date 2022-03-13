from flask import Flask, render_template , request , jsonify
from PIL import Image
import base64

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

@app.route('/webTier' , methods=['POST'])
def webTier():
	file = request.files['myfile']
	app.logger.debug("File name recevied %s", file.filename)
	key = file.filename
	value = base64.b64encode(file.read())
	# task_cb = Process(target=run_task, args=( key, value))
    # task_cb.start()
	return jsonify({'key':str(key), 'value': str(value)})


@app.route("/")
def main():
    app.logger.debug("debug")
    app.logger.info("info")
    return "", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=6060)
