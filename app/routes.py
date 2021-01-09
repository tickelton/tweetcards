import os
import sys
import uuid
import logging
import tempfile
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


MAX_CHARS_HEADLINE = 43
MAX_CHARS_SYNOPSIS = 60
THUMB_IMAGE_WIDTH = 123
THUMB_IMAGE_HEIGHT = 123
VALID_IMAGE_EXTENSIONS  = {'jpg', 'jpeg', 'gif', 'png'}

def is_image_type(filename):
    ''' Checks if file name has a valid extension '''

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in VALID_IMAGE_EXTENSIONS

def create_thumb_image(image_path):
    ''' Crops the input image to a square and resizes it '''

    im = Image.open(image_path)
    (width, height) = im.size

    if width < THUMB_IMAGE_WIDTH or height < THUMB_IMAGE_HEIGHT:
        raise ValueError(
            'Minimum image size: {}x{}px (got {}x{})'.format(
                THUMB_IMAGE_WIDTH,
                THUMB_IMAGE_HEIGHT,
                width,
                height
            )
        )

    if width > height:
        im_square = im.crop(
                (
                    (width-height)/2,
                    0,
                    width-(width-height)/2,
                    height
                )
        )
    else:
        im_square = im.crop(
                (
                    0,
                    (height-width)/2,
                    width,
                    height-(height-width)/2,
                )
        )

    im_resized = im_square.resize((THUMB_IMAGE_WIDTH, THUMB_IMAGE_HEIGHT))

    return im_resized


@app.route('/')
@app.route('/index')
def upload_form():
    return render_template(
        'index.html',
        maxlength_headline=MAX_CHARS_HEADLINE,
        maxlength_synopsis=MAX_CHARS_SYNOPSIS
    )


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
def display_image():
    f = request.files['file']
    headline = request.form['headline']
    synopsis = request.form['synopsis']

    if f.filename == '':
        flash('No image file selected')
        return redirect(request.url)

    if not headline or not synopsis:
        flash('No text supplied')
        return redirect(request.url)

    if f and is_image_type(f.filename):
        #app.logger.info("INFO LOG")

        # generate generic name for the uploaded
        # image and save it in a temporary directory
        extension = f.filename.rsplit('.', 1)[1].lower()
        save_name_base = str(uuid.uuid4().hex)
        save_name = save_name_base + "." + extension
        tempdir = tempfile.TemporaryDirectory()
        save_path = os.path.join(tempdir.name, save_name)
        f.save(save_path)

        try:
            image_thumb = create_thumb_image(save_path)
        except ValueError as e:
            flash(str(e))
            tempdir.cleanup()
            return redirect(request.url)

        img = Image.new('RGBA', (568, 123), 'white')
        d = ImageDraw.Draw(img)
        font_headline = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 18)
        d.text((180, 30), headline, fill=(0, 0, 0), font=font_headline)
        font_synopsis = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 15)
        d.text((180, 70), synopsis, fill=(0, 0, 0), font=font_synopsis)
        img.paste(image_thumb, (0, 0))

        outer_corner = Image.new("L", (11,11), 0)
        draw_outer_corner = ImageDraw.Draw(outer_corner)
        draw_outer_corner.pieslice((0,0, 22, 22), 180, 270, 'white')
        inner_corner = Image.new("L", (11,11), 0)
        draw_inner_corner = ImageDraw.Draw(inner_corner)
        draw_inner_corner.pieslice((0,0, 23, 23), 180, 270, 'white')
        mask_im_outer = Image.new("L", (570,125), 'white')
        mask_im_outer.paste(outer_corner, (0,0))
        mask_im_outer.paste(outer_corner.rotate(90), (0, 125-11))
        mask_im_outer.paste(outer_corner.rotate(180), (570-11, 125-11))
        mask_im_outer.paste(outer_corner.rotate(270), (570-11, 0))

        mask_im_inner = Image.new("L", (568,123), 'white')
        mask_im_inner.paste(inner_corner, (0,0))
        mask_im_inner.paste(inner_corner.rotate(90), (0, 123-11))
        mask_im_inner.paste(inner_corner.rotate(180), (568-11, 123-11))
        mask_im_inner.paste(inner_corner.rotate(270), (568-11, 0))

        target_im = Image.new('RGBA', (570, 125), 'black')
        target_im.putalpha(0)

        border_im = Image.new('RGBA', (570, 125), 'grey')
        target_im.paste(border_im, (0, 0), mask_im_outer)
        target_im.paste(img, (1, 1), mask_im_inner)


        out_name = save_name_base + '.png'
        target_im.save(os.path.join(app.config['UPLOAD_DIR'], out_name))

        tempdir.cleanup()
        return render_template(
            'index.html',
            filename=out_name,
            maxlength_headline=MAX_CHARS_HEADLINE,
            maxlength_synopsis=MAX_CHARS_SYNOPSIS
        )   
    else:
        flash('Supported image types: {}'.format(VALID_IMAGE_EXTENSIONS))
        return redirect(request.url)



