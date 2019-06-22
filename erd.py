#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import json

from flask import Flask, redirect, request
from flask import render_template

app = Flask(__name__)

default_erd_source = '''
# Entities are declared in '[' ... ']'. All attributes after the entity header
# up until the end of the file (or the next entity declaration) correspond
# to this entity.
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

# Each relationship must be between exactly two entities, which need not
# be distinct. Each entity in the relationship has exactly one of four
# possible cardinalities:
#
# Cardinality    Syntax
# 0 or 1         ?
# exactly 1      1
# 0 or more      *
# 1 or more      +
Person *--1 `Birth Place`
'''

def gen_image(source_code, image_path):
    pobj = subprocess.Popen([os.path.expanduser("~/.cabal/bin/erd"), "--fmt=png", "--output=" + image_path],
                            stdin=subprocess.PIPE,
                            #stdout=subprocess.PIPE
    )
    pobj.stdin.write(source_code.encode('utf-8'))
    pobj.stdin.close()
    response = app.make_response(pobj.stdout.read())
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/')
def index():
    return redirect('/static/erd-repl.html')

@app.route('/erds/<id>', methods=['GET', 'PUT'])
def erd(id):
    if "PUT" == request.method:
        obj = json.loads(request.get_json())
        path = "./static/erd-images/" + obj.id # TODO
        gen_image(obj.sourceCode, path)

        returnObj = {
            "imageUri": '/static/erd-images/' + obj.id, # TODO
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
    app.run(debug=True)
