import os
import sqlite3
import random
import shutil
import subprocess as sp
import pytz
import json

from dateutil    import parser
from random      import shuffle
from thumbnailer import get_thumbnail_path

from secret import STATIC_PATH, DB_PATH, DB_FORMAT

from flask import Flask, render_template, request

app = Flask(__name__, static_folder=STATIC_PATH)
app.debug = True
PREFERRED_FORMATS = ['mov', 'mp4', 'webm', 'jpg', 'gif', 'mkv', 'png']

def get_time_for_vid(video_path):
    command = ["ffprobe", "-loglevel",  "quiet", "-print_format", "json", "-show_format", "-show_streams", os.path.join(STATIC_PATH, video_path)]
    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    out, err = pipe.communicate()
    output = json.loads(out)
    try:
        ct = output.get('format').get('tags').get('creation_time')
    except AttributeError:
        with open('errfmt.log', 'a') as errfmt:
            errfmt.write(str(output))
            return
    if not ct:
        return
    parsed_time = parser.parse(ct)
    eastern = pytz.timezone('US/Eastern')
    local_time = parsed_time.astimezone(eastern)
    time_fmt = '%b %d %y %I:%M%p %a'
    return local_time.strftime(time_fmt)

def preferred_format_check(s):
    for fmt in PREFERRED_FORMATS:
        if fmt in s.lower():
            return True
    return False

def fetch_tags(video_name, db=None, as_string=True):
    if not db:
        conn = sqlite3.connect(DB_PATH)
        db = conn.cursor()

    db_index = DB_FORMAT.format(video_name)
    if as_string:
        return ','.join(tag[0] for tag in db.execute("SELECT tag from videos where video=?", (db_index,)))
    else:
        return [tag[0] for tag in db.execute("SELECT tag from videos where video=?", (db_index,))]

def get_video_meta(video_name, tag=None):
    if tag:
        videos = [x[0] for x in get_videos_for_tag(tag)]
    else:
        videos = sorted((m for m in os.listdir(STATIC_PATH) if preferred_format_check(m)))
    try:
        i = videos.index(video_name)
    except ValueError:
        videos.append(video_name)
        videos.sort()
        i = videos.index(video_name) - 1
        videos.remove(video_name)
        video_name = videos[i]
    t = get_time_for_vid(video_name)

    return {
            'next': videos[(i + 1) % len(videos)],
            'last': videos[i - 1],
            'time': t,
            'video_name': video_name
    }
    

@app.route('/tag', methods=['POST'])
def add_tag():
    try:
        tag = request.json['tag']
        video = request.json['video']
        db_index = DB_FORMAT.format(video)
    except (AttributeError, KeyError):
        return('', 400)
    conn = sqlite3.connect(DB_PATH)
    db = conn.cursor()
    db.execute("insert into videos(video, tag) values (?, ?)", (db_index, tag))
    conn.commit()
    return ('', 204)

def get_videos():
    conn = sqlite3.connect(DB_PATH)
    db = conn.cursor()
    videos = sorted(((m, fetch_tags(m, db, as_string=False), get_thumbnail_path(m))
                      for m in os.listdir(STATIC_PATH) if preferred_format_check(m) and not m.startswith('.')), 
                      key=lambda x: x[0]
                   )
    return videos

@app.route('/')
def show_videos():
    videos = get_videos()
    return render_template('index.html', videos=videos)

def get_videos_for_tag(tag_name):
    tag_name = tag_name.split('+')
    videos = get_videos()
    videos = filter(lambda x: all([tag in x[1] for tag in tag_name]), videos)
    return videos

@app.route('/tag/<tag_name>')
def show_videos_for_tag(tag_name=None):
    videos = get_videos_for_tag(tag_name)
    return render_template('index.html', videos=videos, tag_mode=True, tag=tag_name)

@app.route('/tag/<tag>/video/<video>')
def video_view_for_tag(video=None, tag=None):
    tags_for_video = fetch_tags(video, as_string=False)
    meta = get_video_meta(video, tag)
    return render_template('video.html', video_path=video, tags=tags_for_video, meta=meta, tag_mode=True, tag=tag)

@app.route('/tag/<tag>/rando')
def rando_video_for_tag(tag=None):
    videos = list(get_videos_for_tag(tag))
    video = videos[random.randint(0, len(videos))]
    meta = get_video_meta(video[0], tag)
    return render_template('video.html', video_path=video[0], tags=video[1], meta=meta)

@app.route('/videos/<video>')
def show_video(video=None):
    tags_for_video = fetch_tags(video, as_string=False)
    meta = get_video_meta(video)
    if video != meta['video_name']:
        video = meta['video_name']
    return render_template('video.html', video_path=video, tags=tags_for_video, meta=meta)

@app.route('/rando')
def random_video():
    videos = get_videos()
    video = videos[random.randint(0, len(videos))]
    tags_for_video = fetch_tags(video, as_string=False)
    meta = get_video_meta(video[0])
    return render_template('video.html', video_path=video[0], tags=tags_for_video, meta=meta)

