#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/compile')
def gen_image():
    pobj = subprocess.Popen([os.path.expanduser("~/.cabal/bin/erd"), "--fmt=png", "--edge=spline"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    erd_source = '''
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
    pobj.stdin.write(erd_source.encode('utf-8'))
    pobj.stdin.close()
    response = app.make_response(pobj.stdout.read())
    response.headers.set('Content-Type', 'image/png')
    return response