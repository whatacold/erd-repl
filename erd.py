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
app.secret_key = b"B\x9fT\x80/\xf1'\xda9\x1f\xa4\xec>0\x8c-" # os.urandom(16)

def random_string(len=12):
    '''Generate a random string of LEN length, whose characters may
    be ASCII characters and digits.'''
    candidates = string.ascii_letters + string.digits
    return ''.join(random.choice(candidates) for i in range(len))

# TODO moved into some config
default_erd_image = 'default.png'
default_erd_source = '''
title {label: "nfldb Entity-Relationship diagram (condensed)", size: "20"}

# Nice colors from Erwiz:
# red #fcecec
# blue #ececfc
# green #d0e0d0
# yellow #fbfbdb
# orange #eee0a0

# Entities

[player] {bgcolor: "#d0e0d0"}
  *player_id {label: "varchar, not null"}
  full_name {label: "varchar, null"}
  team {label: "varchar, not null"}
  position {label: "player_pos, not null"}
  status {label: "player_status, not null"}

[team] {bgcolor: "#d0e0d0"}
  *team_id {label: "varchar, not null"}
  city {label: "varchar, not null"}
  name {label: "varchar, not null"}

[game] {bgcolor: "#ececfc"}
  *gsis_id {label: "gameid, not null"}
  start_time {label: "utctime, not null"}
  week {label: "usmallint, not null"}
  season_year {label: "usmallint, not null"}
  season_type {label: "season_phase, not null"}
  finished {label: "boolean, not null"}
  home_team {label: "varchar, not null"}
  home_score {label: "usmallint, not null"}
  away_team {label: "varchar, not null"}
  away_score {label: "usmallint, not null"}

[drive] {bgcolor: "#ececfc"}
  *+gsis_id {label: "gameid, not null"}
  *drive_id {label: "usmallint, not null"}
  start_field {label: "field_pos, null"}
  start_time {label: "game_time, not null"}
  end_field {label: "field_pos, null"}
  end_time {label: "game_time, not null"}
  pos_team {label: "varchar, not null"}
  pos_time {label: "pos_period, null"}

[play] {bgcolor: "#ececfc"}
  *+gsis_id {label: "gameid, not null"}
  *+drive_id {label: "usmallint, not null"}
  *play_id {label: "usmallint, not null"}
  time {label: "game_time, not null"}
  pos_team {label: "varchar, not null"}
  yardline {label: "field_pos, null"}
  down {label: "smallint, null"}
  yards_to_go {label: "smallint, null"}

[play_player] {bgcolor: "#ececfc"}
  *+gsis_id {label: "gameid, not null"}
  *+drive_id {label: "usmallint, not null"}
  *+play_id {label: "usmallint, not null"}
  *+player_id {label: "varchar, not null"}
  team {label: "varchar, not null"}

[meta] {bgcolor: "#fcecec"}
  version {label: "smallint, null"}
  season_type {label: "season_phase, null"}
  season_year {label: "usmallint, null"}
  week {label: "usmallint, null"}

# Relationships

player      *--1 team
game        *--1 team {label: "home"}
game        *--1 team {label: "away"}
drive       *--1 team
play        *--1 team
play_player *--1 team

game        1--* drive
game        1--* play
game        1--* play_player

drive       1--* play
drive       1--* play_player

play        1--* play_player

player      1--* play_player
'''

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
    pobj = subprocess.Popen([os.path.expanduser("~/.cabal/bin/erd"), "--fmt=png", "--output=" + image_path],
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
            sourceCode = default_erd_source
            imageFileName = default_erd_image

        obj = {
            "id": userid,
            "sourceCode": sourceCode,
            "imageUri": "/static/erd-images/" + imageFileName + "?t=" + str(time.time()),
        }
        return json.dumps(obj)

if __name__ == '__main__':
    random.seed()
    app.run(debug=True)
