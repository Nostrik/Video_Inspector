import sys
import argparse
import subprocess
import configparser

config = configparser.ConfigParser()


def save_language_config(language):
    config['settings'] = {'language': language}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def get_language_config():
    config.read('config.ini')
    language = config.get('settings', 'language')
    return language


def build_docker_command(path, use_gpu, language, verbose):
    base_command = ["docker", "run", "-it", "-v", f"{path}:/app/files"]
    if use_gpu:
        base_command.extend(["--gpus", "all"])
    base_command.append("dockworker")
    base_command.extend(["-p", f"{path}", "-lang", f"{language}"])
    if verbose:
        base_command.append('-v')
    return base_command


def execute_command(command, verbose):
    if verbose:
        print(command)
    return_code = subprocess.call(command)


def main(args):
    # path = 'C:\\Users\\Maxim\\tv-21-app\\my-tv21-app\\input'
    path  = input('path: ').replace('\r','')
    if args.lang:
        save_language_config(args.lang)
    try:
        language = get_language_config()
    except configparser.NoSectionError:
        save_language_config('en')
        language = get_language_config()

    docker_command = build_docker_command(path, not args.no_gpu, language, args.verbose)
    execute_command(docker_command, args.verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Video-Content-Inspector', description='Video inspector runner')
    parser.add_argument('-v', dest='verbose', action='store_true', required=False, help='verbose option')
    parser.add_argument('-no_gpu', dest='no_gpu', action='store_true', required=False, help='no gpu option')
    parser.add_argument('-lang', choices=["en", "ru"], required=False, help='language(en, ru)')
    args = parser.parse_args()
    main(args)
