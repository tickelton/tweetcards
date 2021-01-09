import logging
from flask import Flask

UPLOAD_DIR = 'app/static/uploads/'

app = Flask(__name__)
app.secret_key = 'secret key'
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.logger.setLevel(logging.DEBUG)

from app import routes
