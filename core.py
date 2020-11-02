import json
import os

import ffmpy

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)


def compression(source_file, input_file, quality, path_to_ffmpeg):
    if not path_to_ffmpeg:
        path_to_ffmpeg = CONFIG['ffmpeg']
    ff = ffmpy.FFmpeg(
        executable=path_to_ffmpeg,
        global_options=None,
        inputs={source_file: None},
        outputs={input_file: '-strict -2 -vf scale=-2:%s' % quality})
    ff.run()


def get_parameters(filename, path_to_ffprobe):
    if not path_to_ffprobe:
        path_to_ffprobe = CONFIG['ffprobe']
    ff = ffmpy.FFprobe(
        executable=path_to_ffprobe,
        global_options=['-v error -select_streams v:0 -show_entries stream=width,height,duration -of json'],
        inputs={filename: None}
    )
    with open('temp.json', 'w') as f:
        info = ff.run(stdout=f)
    with open('temp.json', 'r') as f:
        return json.load(f)
