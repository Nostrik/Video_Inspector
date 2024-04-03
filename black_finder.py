import subprocess
import re
import os
from datetime import datetime
from multiprocessing import Lock
from loguru import logger

from loader import dictionary
from frame2timecode import video_duration


def test_cuda():
    result = subprocess.run(['ffmpeg', '-decoders'], capture_output=True)
    output = result.stdout.decode()

    if 'h264_cuvid' in output:
        return True
    else:
        return True
    

def create_result_file(data, video_file_name, target_folder, object_name):
    cnt = str(len(data))
    txt_file_name = cnt + ' ' + str(object_name).replace('.pt', ' ').replace('\\', '') + str(datetime.now())[:19].replace(' ', ' ').replace(':', '') + ".txt"
    header_name = f"{str(datetime.now())[:19]} | {str(object_name).replace('.pt', '')} | {str(video_file_name).replace('.', '')}"
    file_path = os.path.join(target_folder, txt_file_name)
    logger.debug(f'file_name is ({txt_file_name})')
    logger.debug(f'header_name is ({header_name})')
    logger.debug(f'target_folder is ({target_folder})')
    with open(file_path, "w+", encoding="utf-8") as txt_file:
        txt_file.write(header_name + "\n")
        for i in data:
            # txt_file.write(f'Чёрный кадр с {i[0]:.3f} сек. - {i[1]:.3f} сек. (длительность {i[2]:.3f} сек.)\n')
            txt_file.write(f"{dictionary['minor_phrases'][15]} {i[0]} {dictionary['minor_phrases'][16]}. - {i[1]} {dictionary['minor_phrases'][16]}. ({dictionary['minor_phrases'][17]} {i[2]:.3f} {dictionary['minor_phrases'][16]})\n")


def black_frame_detect_with_multiprocess(weight_file=None, video_path='', object_name=None, queue=None, quantity_processes=None, final_results=None, info_container=None, process_number=0, target_folder=''):
    logger.debug(f"video_path is ({video_path})")
    command = ['ffmpeg', '-i',  video_path, '-filter_complex', 'blackdetect=d=0.1:pix_th=0.05', '-f', 'null', '-']

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    bf=[]
    frame_pattern = re.compile(r'^frame=(\d+)\b.*fps=')
    fps_pattern = re.compile(r'^.*fps=(\d+(?:\.\d+)?)\b.*$')
    time_pattern = re.compile(r'^.*time=(\d\d:\d\d:\d\d\.\d\d).*')

    process_lock = Lock()
    info_dict = {
        "process": process_number,
        "object": "\\black-frame",
        "progress": "",
        "remaining_time": "",
        "recognized_for": "~",
        "process_completed": False,
    }
    info_container

    total_t= video_duration(video_path)
    for line in process.stdout:
        if line.startswith('frame='):
            match_frame = frame_pattern.match(line)
            if match_frame:
                current_frame = int(match_frame.group(1))
            match_fps = fps_pattern.match(line)
            if match_fps:
                fps = float(match_fps.group(1))
            match_time = time_pattern.match(line)           
            if match_time:
                time_str = match_time.group(1)
                time_dt = datetime.strptime(time_str, '%H:%M:%S.%f')
                time_r = (time_dt - datetime(1900, 1, 1)).total_seconds()
            t_progress = round(time_r / total_t * 100, 1)
            info_dict['progress'] = str(t_progress)
            logger.debug(t_progress)
            if t_progress == 100: 
                info_dict['process_completed'] = True
        else:
            match = re.search(r'black_start:([\d\.]+) black_end:([\d\.]+) black_duration:([\d\.]+)', line)
            if match:
                start = float(match.group(1))
                end = float(match.group(2))
                duration = float(match.group(3))
                bf+=[[start,end,duration]]
        # t_progress = str(round(time_r / total_t * 100, 1))
        # info_dict['progress'] = t_progress
        info_dict['remaining_time'] = '~'
        with process_lock:
            try:
                info_container[process_number] = info_dict
            except Exception as e:
                # print(e)s
                pass
        logger.debug(info_dict)
        try:
            queue.put(process_number, info_container)
        except Exception:
            pass
    create_result_file(data=bf, video_file_name=video_path, target_folder=target_folder, object_name='black-frame')
