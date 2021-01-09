tweetcards
==========

tweetcards is a simple flask app that generates preview images
of links for use in microblogs and social media.  
The generated image includes a thumbnail preview image, an
headline and a line of synopsis or a link to the target site.

This is an example of what the output looks like:  
![tweetcard.png](https://gitlab.com/tickelton/tweetcards/raw/master/contrib/tweetcard.png)


Dependencies
------------

tweetcard requires at least Python 3.7 as well as flask and Pillo.  
A Pipfile is provided that can be used to install the required dependencies.


Deployment
----------

A pipenv containing the required dependencies can be set up by running

```shell
pipenv install
```

A development webserver can be started with

```shell
make run
```

The development webserver should not be used in production!


Usage
-----

After starting the development webserver the application can be accessed at   
http://localhost:5000

A tweetcard can be generated by selecting a preview image to upload
and entering a headline and/or synopis/link into the form on the website:

![tweetcards_screenshot.png](https://gitlab.com/tickelton/tweetcards/raw/master/contrib/tweetcards_screenshot.png)


LICENSE
-------

tweetcards is distributed under the terms of the ISC license.

See LICENSE for details.

