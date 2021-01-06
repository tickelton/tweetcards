import os
from flask import render_template, request
from app import app

#>>> from PIL import Image
#>>> im = Image.open('./input.png')
#>>> im.size
#(805, 502)
#>>> outfile = im.resize((100,100))
#>>> outfile.save('./out.png')



@app.route('/')
@app.route('/index')
def upload_form():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
def display_image():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_DIR'], 'foo.png'))
    return render_template('index.html', filename='foo.png')



