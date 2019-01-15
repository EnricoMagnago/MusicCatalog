#! /usr/bin/python3

from flask import Flask, Response, request
from flask import jsonify
from db.music_sheet import MusicSheet, MusicSheetMgr
from db.session_manager import SessionManager
from db.json_encoder import GBCJSONEncoder
import datetime

app = Flask(__name__)
app.json_encoder = GBCJSONEncoder
session_mgr = SessionManager()


@app.route("/")
def hello():
    return "<html><body>" \
           "<h1 style='color:blue'>Hello There!</h1>" \
           "<h2>General Kenobi</h2>" \
           "</body></html>"


@app.route("/api/music_sheet/search", methods=['GET', 'POST'])
def search_music_sheet():
    date_format = "%d-%m-%Y"
    url_args = request.values
    title = None
    composer = None
    arranger = None
    date_added_min = None
    date_added_max = None
    retval = True
    retval_msg = ""
    retval_data = []
    if retval and 'title' in url_args.keys():
        title = url_args['title'].strip()
    if retval and 'composer' in url_args.keys():
        composer = url_args['composer'].strip()
    if retval and 'arranger' in url_args.keys():
        arranger = url_args['arranger'].strip()
    if retval and 'date_added_min' in url_args.keys():
        date_added_min = url_args['date_added_min'].strip()
        try:
            date_added_min = datetime.datetime.strptime(date_added_min,
                                                        date_format)
        except ValueError:
            date_added_min = None
            retval = False
            retval_msg = f"Failed to parse min date, use format: {date_format}"
    if retval and 'date_added_max' in url_args.keys():
        date_added_max = url_args['date_added_max'].strip()
        try:
            date_added_max = datetime.datetime.strptime(date_added_max,
                                                        date_format)
        except ValueError:
            date_added_max = None
            retval = False
            retval_msg = f"Failed to parse max date, use format: {date_format}"

    if retval:
        print(f"query title: "
              f"{title}, composer: {composer}, arranger: {arranger}, "
              f"date_added_min: {date_added_min}, "
              f"date_added_max: {date_added_max}")
        with session_mgr as session:
            retval_data = \
                MusicSheetMgr.search(session, title=title, composer=composer,
                                     arranger=arranger,
                                     date_added_min=date_added_min,
                                     date_added_max=date_added_max)
    return jsonify(retval=retval, msg=retval_msg,
                   data=retval_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
