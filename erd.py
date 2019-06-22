#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import json
import random

from flask import Flask, redirect, request
from flask import render_template

app = Flask(__name__)

default_erd_source = '''
[Person]
*name
height
weight
`birth date`
+birth_place_id

[`Birth Place`]
*id
`birth city`
'birth state'
"birth country"

Person *--1 `Birth Place`
'''

def gen_image(source_code, image_path):
    pobj = subprocess.Popen([os.path.expanduser("~/.cabal/bin/erd"), "--fmt=png", "--output=" + image_path],
                            stdin=subprocess.PIPE,
                            #stdout=subprocess.PIPE
    )
    pobj.stdin.write(source_code.encode('utf-8'))
    pobj.stdin.close()
    return
    response = app.make_response(pobj.stdout.read())
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/')
def index():
    return redirect('/static/erd-repl.html')

@app.route('/erds/<id>', methods=['GET', 'PUT'])
def erd(id):
    if "PUT" == request.method:
        obj = request.get_json() # TODO how to print debug log?
        path = "./static/erd-images/" + obj["id"] + ".png" # TODO
        gen_image(obj["sourceCode"], path)

        returnObj = {
            "imageUri": '/static/erd-images/' + obj["id"] + ".png?" + str(random.randrange(1000000)), # TODO
        }
        return json.dumps(returnObj)
    else:
        obj = {
            "id": id,
            "sourceCode": default_erd_source,
            "imageUri": "/static/erd-images/" + id + ".png", # TODO
        }
        return json.dumps(obj)

if __name__ == '__main__':
    random.seed()
    app.run(debug=True)
