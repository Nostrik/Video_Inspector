import subprocess
import json
from tqdm import tqdm
import re

def video_duration(video_path):

    command = ['ffprobe', video_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1']

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    output = process.stdout.read()
    match = re.search(r'([\d\.]+)', output)
    if match:
        return float(match.group(1))

def f2t(video_path):
    frames_dict = {}
    command = ['ffprobe', video_path, '-hide_banner', '-show_entries', 'frame=coded_picture_number,best_effort_timestamp_time', '-of', 'json']

    print("Генерация тайм кодов..")

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

    output = ""
    frame=0
    timecode=0

    bar=tqdm(total=round(video_duration(video_path),1))

    for line in iter(process.stdout.readline, ''):
        linst = line.strip()

        match = re.search(r'"best_effort_timestamp_time": "([\d\.]+)"', linst)
        if match:
            timecode = float(match.group(1))
        match = ''
        match = re.search(r'"coded_picture_number": (\d+)', linst)
        if match:
            frame = float(match.group(1))

        bar.n = round(timecode, 1)
        bar.refresh()

        output+=linst    


    return_code = process.wait()

    data = json.loads(output)

    frames_dict = {}
    for frame in data['frames']:
        if len(frame)>1:
            frames_dict[frame['coded_picture_number']] = float(frame['best_effort_timestamp_time'])
            
    return frames_dict


# if __name__ == "main":
#     a = video_duration('C:\\Users\Maxim\\tv-21-app\\my-tv21-app\\input\\Shitfest.mp4')
#     print(a)
