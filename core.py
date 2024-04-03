import os
import sys
import time
import subprocess
import shutil
# from loguru import logger
from datetime import datetime
from multiprocessing import Lock
from termcolor import colored
from functools import reduce

from models import NeuralNetwork, NWorker, Line
from frame_temp import current_frame_to_single_frame, NumberChecker, check_number


class NWorkerYoloV8(NWorker):
    out_listing = []

    def __init__(self, network_model, line_model):
        self.netwok_model = network_model
        self.line_model = line_model
        self.start_time = None

    def load_network_model(self, n_model):
        self.netwok_model = n_model
    
    def load_line_model(self, l_model):
        self.line_model = l_model

    def show_progress_results(self):
        progress = self.remainig_progress(
            self.line_model.get_current_position(),
            self.line_model.get_total_amount()
        )
        if self.line_model.get_current_position():
            current_position = int(self.line_model.get_current_position())
            elapsed_time = time.time() - self.start_time
            avg_time_per_iteration = elapsed_time / current_position
            remaining_time = avg_time_per_iteration * (int(self.line_model.get_total_amount()) -  current_position)
            time_in_seconds_minutes_hours = self.transform_time(remaining_time)
        else:
            time_in_seconds_minutes_hours = None
        if self.line_model.get_processing_time():
            processing_time = self.line_model.get_processing_time()
        else:
            processing_time = None
        return self.netwok_model.object_search, processing_time, progress, time_in_seconds_minutes_hours
    
    def catch_find_objects(self, all):
        detected_obj_value_from_line = self.line_model.get_getected_objects()
        if all and detected_obj_value_from_line is not None:
            self.update_listing([detected_obj_value_from_line, self.catch_time_frame(self.line_model.get_current_position())])
        else:
            if detected_obj_value_from_line != '(no detections)' and detected_obj_value_from_line is not None:
                self.update_listing([detected_obj_value_from_line, self.catch_time_frame(self.line_model.get_current_position())])


    def set_start_time(self, start_time):
            self.start_time = start_time

    def transform_time(self, value):
        if value:
            if value < 60:
                updt_value = f'{value:.0f} sec'
            elif value < 3600:
                updt_value = f'{value/60:.0f} min'
            else:
                updt_value = f'{value/3600:.0f} hours'
            return updt_value
        
    def catch_time_frame(self, value):
        if value:
            frame_fl = float(value)
            seconds = frame_fl // 24
            minutes = seconds // 60
            hours = minutes // 60
            minutes %= 60
            seconds %= 60
            return [seconds, minutes, hours, current_frame_to_single_frame(value), value]

    def remainig_progress(self, cur_frm, all_frms):
        if cur_frm and all_frms:
            progress = (float(cur_frm) / float(all_frms)) * 100
            result = round(progress, 0)
            return str(result).replace('.0', '')
        
    def run_predict(self, start_time):
        self.start_time = start_time
        process = self.netwok_model.run_predict()
        return process
    
    def generate_path(self, weight_f, target_v):
        weight_f_path = os.path.dirname(weight_f)
        target_v_path = os.path.dirname(target_v)
        path = os.path.join(weight_f_path, target_v_path)
        return path
    
    def update_listing(self, catch_info):
        self.out_listing.append(catch_info)

    def reset_listing(self):
        self.out_listing = []

    def take_output_results(self):
        results = self.out_listing
        for res in results:
            print(res)

    def get_result_name(self, weigth_file, target_video, object_name, current_folder):
        cnt = str(len(self.out_listing))
        optimized_object_name = reduce(lambda x, char: x.replace(char, ''), [
            '.pt', '\\',
        ], str(object_name))
        optimized_datetime = reduce(lambda x, char: x.replace(char, ''), [
            ' ', ':',
        ], str(datetime.now())[:19])
        optimized_target_video = reduce(lambda x, char: x.replace(char, ''), [
            '.', 'files', '/',
        ], str(target_video))
        optimized_weight_file = reduce(lambda x, char: x.replace(char, ''), [
            '.pt', 'files', '/',
        ], str(weigth_file))
        result_name = cnt + '_' + optimized_object_name + '_' + optimized_target_video
        header_name = f"{str(datetime.now())[:19]} | {optimized_weight_file} | {optimized_target_video}"
        return result_name, header_name

    def create_result_file(self, weigth_file, target_video, object_name, current_folder, result_name):
        time.sleep(1)

        cnt = str(len(self.out_listing))
        optimized_object_name = reduce(lambda x, char: x.replace(char, ''), [
            '.pt', '\\',
        ], str(object_name))
        optimized_datetime = reduce(lambda x, char: x.replace(char, ''), [
            ' ', ':',
        ], str(datetime.now())[:19])
        txt_file_name = cnt + ' ' + optimized_object_name + optimized_datetime + ".txt"

        optimized_weight_file = reduce(lambda x, char: x.replace(char, ''), [
            '.pt', 'files', '/',
        ], str(weigth_file))
        optimized_target_video = reduce(lambda x, char: x.replace(char, ''), [
            '.', 'files', '/',
        ], str(target_video))
        header_name = f"{str(datetime.now())[:19]} | {optimized_weight_file} | {optimized_target_video}"
        # target_folder = os.path.join(
        #     os.path.dirname(weigth_file),
        #     os.path.dirname(target_video)
        # )
        # logger.debug(f'file_name is ({txt_file_name})')
        # logger.debug(f'header_name is ({header_name})')
        # logger.debug(f'current_folder is ({current_folder})')
        count_srtings = 0
        with open(os.path.join(current_folder, txt_file_name), "w+", encoding="utf-8") as txt_file:
            txt_file.write(header_name + "\n")
            for v in self.out_listing:
                txt_file.write(f"{v[0]}, [{v[1][0]} sec | {v[1][1]} min | {v[1][2]} hour | {v[1][3]} frame ({v[1][4]})]\n")
                count_srtings += 1
            txt_file.write(f"cnt: {count_srtings}")

    def create_result_file2(self, name, header, folder_path):
        time.sleep(1)

        cnt = str(len(self.out_listing))
        txt_file_name = name + ".txt"
        count_srtings = 0
        # with open(os.path.join(folder_path, txt_file_name), "w+", encoding="utf-8") as txt_file:
        #     txt_file.write(header + "\n")
        #     for v in self.out_listing:
        #         txt_file.write(f"{v[0]}, [{v[1][0]} sec | {v[1][1]} min | {v[1][2]} hour | {v[1][3]} frame ({v[1][4]})]\n")
        #         count_srtings += 1
        #     txt_file.write(f"cnt: {count_srtings}")
        num_checker = NumberChecker()
        with open(os.path.join(folder_path, txt_file_name), "w+", encoding="utf-8") as txt_file:
            txt_file.write(header + "\n")
            for v in self.out_listing:
                checked_frame_number = num_checker.check_number(v[1][4])
                txt_file.write(f"{v[0]}, [{v[1][0]} sec | {v[1][1]} min | {v[1][2]} hour | {v[1][3]} frame ({v[1][4]})]\n")
                if checked_frame_number == False:
                    txt_file.write("------------------\n")
                count_srtings += 1
            txt_file.write(f"cnt: {count_srtings}")

    def copy_result_folder(self, new_folder_name):
        folder_name = new_folder_name.replace('.txt', '').replace(' ', '_')
        source_folder = "/usr/src/ultralytics/runs/detect/predict"
        destination_folder = f"/app/files/{folder_name}"
        try:
            shutil.copytree(source_folder, destination_folder)
        except Exception as ex:
            print(ex)
        return destination_folder



class YoloNeuralNetwork(NeuralNetwork):
    def __init__(self, model_path, video_path, obj_name) -> None:
        self.model = model_path
        self.video = video_path
        self.object_search = obj_name

    def load_model(self, model_path):
        self.model = model_path

    def preprocess_input(self, video_path):
        self.video = video_path

    def postprocess_output(self, output_data):
        pass

    def run_predict(self):
        PopenPars = [
            "yolo", "predict", f"model={self.model}", f"source={self.video}",
            ]
        return subprocess.Popen(PopenPars, stdout=subprocess.PIPE)

    def get_model(self):
        summary = f"{self.model}"
        print(summary)


class YoloV8Line(Line):
    def __init__(self) -> None:
        self.line = None
        self.values = None

    def update_values(self, new_line):
        self.line = new_line
        self.values = self.extract_values()

    def extract_values(self):
        if not self.line.startswith('video ') or not self.line.endswith('s') or ':' not in self.line:
            return None

        components = self.line.strip().split(' ')
        video_num, video_total = components[1].split('/')
        current_pos, total_amount = components[2][1:-1].split('/')
        path_to_file, rest_of_line = self.line.rsplit(': ', 1)
        path_to_file = path_to_file.split(' ', maxsplit=3)[-1].strip()
        video_size, rest_of_line = rest_of_line.split(' ', maxsplit=1)
        detected_objs = rest_of_line.rsplit(',', maxsplit=1)[0]
        processing_time = rest_of_line.rsplit(',', maxsplit=1)[1].strip()

        return {
            'current_pos': current_pos,
            'total_amount': total_amount,
            'detected_objs': detected_objs,
            'processing_time': processing_time
        }
    
    def show_values(self):
        print(self.values)

    def get_current_position(self):
        if self.values:
            cur_pos = self.values['current_pos']
            return cur_pos
            
    def get_total_amount(self):
        if self.values:
            return self.values['total_amount']

    def get_getected_objects(self):
        if self.values:
            return self.values['detected_objs']

    def get_processing_time(self):
        if self.values:
            return self.values['processing_time']


def terminal_printer(quantity_processes, info_container):
    cursor_up = lambda lines: '\x1b[{0}A'.format(lines)
    time.sleep(5)
    continue_output = True
    while continue_output:
        output = ""
        completed_list = []
        sorted_info_container = sorted(info_container, key=lambda x: x["process"])
        # logger.debug(f"sorted_info_container - ({sorted_info_container})")
        for info_dict in sorted_info_container:
            output += f"Object: {info_dict['object']} | Progress: {info_dict['progress']} % | Remaining Time: {info_dict['remaining_time']} | Processing Time: {info_dict['recognized_for']}"
            output += '\n'
            completed_list.append(info_dict['process_completed'])
        print(colored(output, "yellow"), end='\r')
        # logger.debug(f"len of info_container - {len(sorted_info_container)}")
        # logger.debug(f"output - ({output})")
        if all(completed_list):
            continue_output = False
            break
        time.sleep(0.2)
        print(cursor_up(quantity_processes + 1))


def start_predict(
        weigth_file, target_video, object_name, queue=None, quantity_processes=None, final_results=None, info_container=None, process_number=0, target_folder=''
        ):
    # logger.debug(f"weigth_file - ({weigth_file})")
    # logger.debug(f"target_video - ({target_video})")
    process_lock = Lock()
    info_dict = {
        "process": process_number,
        "object": object_name,
        "progress": "",
        "remaining_time": "",
        "recognized_for": "",
        "process_completed": False,
    }
    info_container

    yolo = YoloNeuralNetwork(
        model_path=weigth_file,
        video_path=target_video,
        obj_name=object_name,
    )
    yolo_line = YoloV8Line()
    yolo_worker = NWorkerYoloV8(
        network_model=yolo,
        line_model=yolo_line,
    )
    process = yolo_worker.run_predict(time.time())
    yolo_worker.reset_listing()
    process_cont = True
    while process_cont:

        output = process.stdout.readline().decode('utf-8')
        yolo_line.update_values(output.strip())
        yolo_worker.catch_find_objects(all=False)
        progress = yolo_worker.show_progress_results()
        object_search, processing_time, progress, time_in_seconds_minutes_hours = yolo_worker.show_progress_results()
        info_dict['progress'] = progress
        info_dict['remaining_time'] = time_in_seconds_minutes_hours
        info_dict['recognized_for'] = processing_time
        if progress:
            if int(progress) >= 100:
                info_dict['process_completed'] = True
                process_cont = False
        with process_lock:
            try:
                info_container[process_number] = info_dict
            except Exception as er:
                # print(f"core:line 269:er {er}")
                exit(0)
        try:
            queue.put(process_number, info_container)
        except Exception as er:
            print(f"core:line 273:er {er}")
            exit(0)

    # resutl_name = yolo_worker.create_result_file(weigth_file, target_video, object_name, target_folder)
    result_name, header_name = yolo_worker.get_result_name(weigth_file, target_video, object_name, target_folder)
    result_folder_path = yolo_worker.copy_result_folder(result_name)
    yolo_worker.create_result_file2(result_name,header_name, result_folder_path)

    # while True:
    #     output = process.stdout.readline().decode('utf-8')
    #     sys.stdout.write(output)
