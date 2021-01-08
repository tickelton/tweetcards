import os
import sys
import uuid
from PIL import Image, ImageDraw, ImageFont
from flask import render_template, redirect, flash, request
from app import app

#>>> from PIL import Image
#>>> im = Image.open('./input.png')
#>>> im.size
#(805, 502)
#>>> outfile = im.resize((100,100))
#>>> outfile.save('./out.png')


#>>> round_corner = Image.new("L", (11,11), 0)
#>>> draw_corner = ImageDraw.Draw(round_corner)
#>>> draw_corner.pieslice((0,0, 22, 22), 180, 270, 'white')
#>>> mask_im1 = Image.new("L", (125,125), 'white')
#>>> mask_im1.paste(round_corner, (0,0))
#>>> mask_im1.paste(round_corner.rotate(90), (0, 114))
#>>> mask_im1.save("mask.png")

# print('DEBUG OUTPUT', file=sys.stderr)


VALID_IMAGE_EXTENSIONS  = {'jpg', 'jpeg', 'gif', 'png'}
def is_image_type(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in VALID_IMAGE_EXTENSIONS


@app.route('/')
@app.route('/index')
def upload_form():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
def display_image():
    f = request.files['file']
    headline = request.form['headline']
    synopsis = request.form['synopsis']

    print("FORM DATA: %s xx %s", headline, synopsis, file=sys.stderr)

    if f.filename == '':
        flash('No image file selected')
        return redirect(request.url)
    if not headline or not synopsis:
        flash('No text supplied')
        return redirect(request.url)
    if f and is_image_type(f.filename):
        extension = f.filename.rsplit('.', 1)[1].lower()
        save_name = str(uuid.uuid4().hex) + "." + extension
        save_path = os.path.join(app.config['UPLOAD_DIR'], save_name)
        #f.save(save_path)

        # TODO: preserve aspect ratio
        #im = Image.open(save_path)
        #im_resized = im.resize((121,121))
        #im_resized.save(save_path)

        img = Image.new('RGBA', (570, 125), 'white')
        # TODO: check text length
        d = ImageDraw.Draw(img)
        font_headline = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 15)
        d.text((180, 30), headline, fill=(0, 0, 0), font=font_headline)
        font_synopsis = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 15)
        d.text((180, 70), synopsis, fill=(0, 0, 0), font=font_synopsis)
        img.save('/tmp/out.png')

        return render_template('index.html', filename=save_name)
    else:
        flash('Supported image types: {}'.format(VALID_IMAGE_EXTENSIONS))
        return redirect(request.url)



