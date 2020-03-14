import subprocess as sp
import json
import os

from secret import STATIC_PATH, DB_PATH, DB_FORMAT

def get_thumbnail_path(video_name, absolute=False):
    video_name = '.'.join(video_name.split('.')[:-1]) + '.png'
    if absolute:
        thumbnail_path = os.path.join(STATIC_PATH, 'thumbnails', video_name)
    else:
        thumbnail_path = "thumbnails/{}".format(video_name)
    return thumbnail_path

def thumbnailer():

    videos = os.listdir(STATIC_PATH)

    # phone
    videos = [m for m in videos if 'MOV' in m]
    thumbnailed_videos = [t.replace('png', 'MOV') for t in os.listdir(os.path.join(STATIC_PATH, 'thumbnails'))]

    # tumblr
    #videos = [m for m in videos if ('tumblr' in m and 'mp4' in m)]
    #thumbnailed_videos = [t.replace('png', 'mp4') for t in os.listdir(os.path.join(STATIC_PATH, 'thumbnails'))]
    videos_not_thumbnailed = [m for m in videos if m not in thumbnailed_videos]

    for video_name in videos_not_thumbnailed:
        video_path = os.path.join(STATIC_PATH, video_name)
        command = ["ffprobe",
                "-loglevel",  "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
                ]

        pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
        out, err = pipe.communicate()
        output = json.loads(out)
        try:
            duration = output.get('format').get('duration')
        except AttributeError:
            try: 
                duration = output.get('streams').get('duration')
            except AttributeError:
                continue

        """
        snapshot_time is now just 10 for most videos because that was faster to make thumbnails for
        """
        if float(duration) > 10:
            snapshot_time = 10
        else:
            snapshot_time = float(duration) / 2

        thumbnail_path = get_thumbnail_path(video_name, absolute=True)

        command = ['ffmpeg', '-i', video_path, '-ss', str(snapshot_time), '-vf', 'scale=128:-1', '-vframes', '1', thumbnail_path]
        print(duration, command)
        sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT)

if __name__ == '__main__':
    thumbnailer()
