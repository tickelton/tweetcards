# Copyright (c) 2021 tick <tickelton@gmail.com>
# SPDX-License-Identifier:	ISC

import os
import sys
import uuid
import logging
import tempfile
from PIL import Image, ImageDraw, ImageFont
from flask import render_template, redirect, flash, request
from app import app


# constants

TWEETCARD_WIDTH = 570
TWEETCARD_HEIGHT = 125
IMAGE_BODY_WIDTH = TWEETCARD_WIDTH - 2
IMAGE_BODY_HEIGHT = TWEETCARD_HEIGHT - 2
IMAGE_BODY_BG = 'white'
MAX_CHARS_HEADLINE = 43
MAX_CHARS_SYNOPSIS = 60
THUMB_IMAGE_WIDTH = IMAGE_BODY_HEIGHT
THUMB_IMAGE_HEIGHT = IMAGE_BODY_HEIGHT
TEXT_X_OFFSET = 180
HEADLINE_Y_OFFSET = 30
SYNOPSIS_Y_OFFSET = 70
FONT_SIZE_SYNOPSIS = 15
FONT_PATH = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
FONT_SIZE_HEADLINE = 18
FONT_BOLD_PATH = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
CORNER_RADIUS = 11
VALID_IMAGE_EXTENSIONS  = {'jpg', 'jpeg', 'gif', 'png'}


# functions

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

def create_image_text(image_thumb, headline, synopsis):
    ''' Creates image with headline and synopsis '''

    # create base image
    image_text = Image.new('RGBA', (IMAGE_BODY_WIDTH, IMAGE_BODY_HEIGHT), IMAGE_BODY_BG)
    d = ImageDraw.Draw(image_text)

    # draw headline
    font_headline = ImageFont.truetype(FONT_BOLD_PATH, FONT_SIZE_HEADLINE)
    d.text((TEXT_X_OFFSET, HEADLINE_Y_OFFSET), headline, fill=(0, 0, 0), font=font_headline)

    # draw synopsis
    font_synopsis = ImageFont.truetype(FONT_PATH, FONT_SIZE_SYNOPSIS)
    d.text((TEXT_X_OFFSET, SYNOPSIS_Y_OFFSET), synopsis, fill=(0, 0, 0), font=font_synopsis)

    # paste thumbnail onto text image
    image_text.paste(image_thumb, (0, 0))

    return image_text

def create_mask_images():
    ''' Creates masks for rounded corners '''

    # create pie slice for outer corners
    outer_corner = Image.new("L", (CORNER_RADIUS, CORNER_RADIUS), 0)
    draw_outer_corner = ImageDraw.Draw(outer_corner)
    draw_outer_corner.pieslice(
        (
            0,
            0,
            CORNER_RADIUS*2,
            CORNER_RADIUS*2
        ),
        180,
        270,
        IMAGE_BODY_BG
    )

    # create pie slice for inner corners
    inner_corner = Image.new("L", (CORNER_RADIUS, CORNER_RADIUS), 0)
    draw_inner_corner = ImageDraw.Draw(inner_corner)
    draw_inner_corner.pieslice(
        (
            0,
            0,
            (CORNER_RADIUS*2)+1,
            (CORNER_RADIUS*2)+1
        ),
        180,
        270,
        IMAGE_BODY_BG
    )

    # create mask imager for outer corners
    mask_im_outer = Image.new("L", (TWEETCARD_WIDTH,TWEETCARD_HEIGHT), IMAGE_BODY_BG)
    mask_im_outer.paste(outer_corner, (0,0))
    mask_im_outer.paste(
        outer_corner.rotate(90),
        (0, TWEETCARD_HEIGHT-CORNER_RADIUS)
    )
    mask_im_outer.paste(
        outer_corner.rotate(180),
        (TWEETCARD_WIDTH-CORNER_RADIUS, TWEETCARD_HEIGHT-CORNER_RADIUS)
    )
    mask_im_outer.paste(
        outer_corner.rotate(270),
        (TWEETCARD_WIDTH-CORNER_RADIUS, 0)
    )

    # create mask image for inner corners
    mask_im_inner = Image.new("L", (IMAGE_BODY_WIDTH,IMAGE_BODY_HEIGHT), IMAGE_BODY_BG)
    mask_im_inner.paste(inner_corner, (0,0))
    mask_im_inner.paste(
        inner_corner.rotate(90),
        (0, IMAGE_BODY_HEIGHT-CORNER_RADIUS)
    )
    mask_im_inner.paste(
        inner_corner.rotate(180),
        (IMAGE_BODY_WIDTH-CORNER_RADIUS, IMAGE_BODY_HEIGHT-CORNER_RADIUS)
    )
    mask_im_inner.paste(
        inner_corner.rotate(270),
        (IMAGE_BODY_WIDTH-CORNER_RADIUS, 0)
    )

    return (mask_im_outer, mask_im_inner)


# routes

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

    # fetch input file and text from form
    f = request.files['file']
    headline = request.form['headline']
    synopsis = request.form['synopsis']

    if f.filename == '':
        flash('No image file selected')
        return redirect(request.url)

    if not headline and not synopsis:
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

        # create thumbnail and image text
        try:
            image_thumb = create_thumb_image(save_path)
        except ValueError as e:
            flash(str(e))
            tempdir.cleanup()
            return redirect(request.url)

        image_text = create_image_text(image_thumb, headline, synopsis)

        (mask_im_outer, mask_im_inner) = create_mask_images()

        # create transparent background for output image
        target_im = Image.new('RGBA', (TWEETCARD_WIDTH, TWEETCARD_HEIGHT), 'black')
        target_im.putalpha(0)

        # past border and content onto base image
        border_im = Image.new('RGBA', (TWEETCARD_WIDTH, TWEETCARD_HEIGHT), 'grey')
        target_im.paste(border_im, (0, 0), mask_im_outer)
        target_im.paste(image_text, (1, 1), mask_im_inner)

        # save output in uploads folder
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



