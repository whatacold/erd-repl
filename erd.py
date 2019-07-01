#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import json
import random
import time
import sys
sys.path.insert(0, "./submodules/")
from PythonUtils import StringUtil

from flask import Flask, redirect, request, session
from flask import render_template

app = Flask(__name__)
app.secret_key = b"B\x9fT\x80/\xf1'\xda9\x1f\xa4\xec>0\x8c-" # os.urandom(16)

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
    #pobj.stdin.close()
    pobj.communicate(timeout=1) # XXX Need this to wait subprocess to terminate
    app.logger.debug("popen return code: {}".format(pobj.returncode)) # TODO handle error
    return
    response = app.make_response(pobj.stdout.read())
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/')
def index():
    userid = ""
    if "userid" in session:
        userid = session["userid"]
        app.logger.debug("cookie userid: %s", userid)
    if len(userid) == 0:
        userid = "user_" + str(time.time()) + StringUtil.random_string()
        session["userid"] = userid
        app.logger.debug("set userid in cookie: %s", userid)
    return render_template('erd-repl.html', userid=userid)

@app.route('/erds/<userid>', methods=['GET', 'PUT'])
def erd(userid):
    if "PUT" == request.method:
        obj = request.get_json()
        imageFileName = obj["id"] + ".png"
        path = "./static/erd-images/" + imageFileName
        gen_image(obj["sourceCode"], path)
        session["sourceCode"] = obj["sourceCode"]

        returnObj = {
            "imageUri": '/static/erd-images/' + imageFileName + "?t=" + str(time.time()),
        }
        return json.dumps(returnObj)
    else:
        sourceCode = default_erd_source
        if "sourceCode" in session:
            sourceCode = session["sourceCode"]
        obj = {
            "id": userid,
            "sourceCode": sourceCode,
            "imageUri": "/static/erd-images/" + userid + ".png" + "?t=" + str(time.time()),
        }
        return json.dumps(obj)

if __name__ == '__main__':
    random.seed()
    app.run(debug=True)
