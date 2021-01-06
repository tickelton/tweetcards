from flask import Flask

UPLOAD_DIR = 'app/static/uploads/'

app = Flask(__name__)
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

from app import routes
