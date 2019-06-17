#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/compile')
def gen_image():
    pobj = subprocess.Popen(["cat", "./google.png"],
                            stdout=subprocess.PIPE,
    )
    response = app.make_response(pobj.stdout.read())
    response.headers.set('Content-Type', 'image/png')
    return response