#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import json
import random
import time
import sys
import string

from flask import Flask, redirect, request, session
from flask import render_template, jsonify

app = Flask(__name__)
app.config.from_pyfile("./config.py")

def random_string(len=12):
    '''Generate a random string of LEN length, whose characters may
    be ASCII characters and digits.'''
    candidates = string.ascii_letters + string.digits
    return ''.join(random.choice(candidates) for i in range(len))

# copied from zapier transformer
class APIError(Exception):
    """ Base Exception for the API """
    status_code = 400

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv

def gen_image(source_code, image_path):
    pobj = subprocess.Popen([os.path.expanduser(app.config["ERD_BIN_PATH"]), "--fmt=png", "--output=" + image_path],
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            #stdout=subprocess.PIPE
    )
    pobj.stdin.write(source_code.encode('utf-8'))
    #pobj.stdin.close()
    _, errInfo = pobj.communicate(timeout=1) # XXX Need this to wait subprocess to terminate
    app.logger.debug("popen return code: {}".format(pobj.returncode)) # TODO handle error
    if pobj.returncode:
        raise APIError("erd syntax error", payload={"error": errInfo.decode('utf-8')})
    return

    response = app.make_response(pobj.stdout.read())
    response.headers.set('Content-Type', 'image/png')
    return response

@app.errorhandler(APIError)
def error(e):
    """ Handle our APIError exceptions """
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response


@app.errorhandler(Exception)
def exception(e):
    """ Handle generic exceptions """
    response = jsonify(message=str(e))
    response.status_code = 500
    return response


@app.route('/')
def index():
    return redirect('/erd-repl/')

@app.route('/erd-repl/')
def erd_repl():
    userid = ""
    if "userid" in session:
        userid = session["userid"]
        app.logger.debug("cookie userid: %s", userid)
    if len(userid) == 0:
        userid = "user_" + str(time.time()) + random_string()
        session["userid"] = userid
        app.logger.debug("set userid in cookie: %s", userid)
    return render_template('erd-repl.html', userid=userid)

@app.route('/erd-repl/erds/<userid>', methods=['GET', 'PUT'])
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
        sourceCode = ""
        imageFileName = ""
        if "sourceCode" in session:
            sourceCode = session["sourceCode"]
            imageFileName = userid + ".png"
        else:
            sourceCode = app.config["DEFAULT_ERD_SOURCE"]
            imageFileName = app.config["DEFAULT_ERD_IMAGE"]

        obj = {
            "id": userid,
            "sourceCode": sourceCode,
            "imageUri": "/static/erd-images/" + imageFileName + "?t=" + str(time.time()),
        }
        return json.dumps(obj)

if __name__ == '__main__':
    random.seed()
    app.run(debug=True)
