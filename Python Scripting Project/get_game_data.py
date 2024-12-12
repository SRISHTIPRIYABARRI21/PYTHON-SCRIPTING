import os
import json  # for json files
import shutil  # copy and overwrite operations
from subprocess import PIPE, run  # import pip and run
import sys  # access to command line directory

GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]


def find_all_game_paths(source):  # will give teh full path with directory path
    game_paths = []

    for root, dirs, files in os.walk(source):  # walk recursively through source directories we passed to the os.walk command
        for directory in dirs:  # gives the name of the directories not the paths
            if GAME_DIR_PATTERN in directory.lower():  # name of the directory
                path = os.path.join(source, directory)  # add this path to my game path 
                game_paths.append(path)  # adds the path of the directories

        break

    return game_paths


def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)  # split the path
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)

    return new_names


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def copy_and_overwrite(source, dest):  # will take source and destination  and copy the sorce into the destination.
    if os.path.exists(dest):
        shutil.rmtree(dest)  # remove the destination folder
    shutil.copytree(source, dest) 


def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }

    with open(path, "w") as f:
        json.dump(data, f)  # dump data into the file


def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:  # in files
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break

        break

    if code_file_name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)


def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)  # PIPE makes the bridge between our python code and the process we are using to run the command
    print("compile result", result)

    os.chdir(cwd)  # current working directory


def main(source, target):
    cwd = os.getcwd()  # current working directory
    source_path = os.path.join(cwd, source)  # os.path.join should be used when try to create a path not copying path manually.
    target_path = os.path.join(cwd, target) 

    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")

    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs):  # will take the matcging elements from 2 arrays and combine them into a tuple. 
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")  # join target data with metadatajson file
    make_json_metadata_file(json_path, new_game_dirs)


if __name__ == "__main__":  # system module
    args = sys.argv  
    if len(args) != 3: 
        raise Exception("You must pass a source and target directory - only.")

    source, target = args[1:]  # 1 is to strip off the name o fthe py file and to get these 2 arguments here and store them in seperate variables.
    main(source, target)
