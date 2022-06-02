#!/usr/bin/env python3

import sys
import subprocess
import os

INVOKE_DIR = os.getcwd()
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.realpath(THIS_DIR + "/../..")
DOCKER_IMAGE_NAME = "litgen_docker_ci_image"
DOCKER_CONTAINER_NAME = "litgen_docker_ci"
SOURCES_MOUNT_DIR = "/dvp/sources"
ONLY_SHOW_COMMAND = False


CHDIR_LAST_DIRECTORY = INVOKE_DIR


def my_chdir(folder):
    global CHDIR_LAST_DIRECTORY
    os.chdir(folder)
    if ONLY_SHOW_COMMAND and folder != CHDIR_LAST_DIRECTORY:
        print(f"cd {folder}")
    CHDIR_LAST_DIRECTORY = folder


def run_local_command(cmd, quiet=False):
    if ONLY_SHOW_COMMAND:
        print(cmd)
    else:
        if not quiet:
            print(f"\n{cmd}\n")
        subprocess.check_call(cmd, shell=True)


def help():
    print(f"""
        Usage: {sys.argv[0]}    -build_image|-create_container|-bash|-remove_container| -remove_image
                              | exec [any command and args] 

                              [--show_command]
        
            {sys.argv[0]} -full_build 
        Will build the image, create and start a container based on this image 
        (any previously running container named {DOCKER_CONTAINER_NAME} will be removed

            {sys.argv[0]} -build_image 
        Will build the image (call this first). It will be called {DOCKER_IMAGE_NAME}

            {sys.argv[0]} -create_container 
        Will create a container called {DOCKER_CONTAINER_NAME} from this image, 
        where the sources are mounted at {SOURCES_MOUNT_DIR}.
        This container will start in detached mode (-d). Call this after build_image. 

            {sys.argv[0]} -recreate_container 
        Will recreate a container called {DOCKER_CONTAINER_NAME} from this image
        and delete any previous container with this name.
        
            {sys.argv[0]} -bash 
        Will log you into a bash session in the previously created container.

            {sys.argv[0]} -build_pip
        Will start the container and build the pip project

            {sys.argv[0]} -remove_container 
        Will remove the container (you will lose all modifications in the Docker container)
        
            {sys.argv[0]} -remove_image 
        Will remove the image

            {sys.argv[0]} exec [any command and args]
        Will start the container and run the commands given after "exec".
        For example, "{sys.argv[0]} exec ls -al" will list the files.  

            {sys.argv[0]} exec_it [any command and args]
        Will start the container and run the commands given after "exec_it" in interactive mode

            --show_command 
        Will not run the command, but show you its command line.
        """)


def run_docker_command(commands, quiet: bool, interactive: bool):
    in_bash_commands = f'/bin/bash -c "{commands}"'
    interactive_flag = "-it" if interactive else ""
    run_local_command(f"docker start {DOCKER_CONTAINER_NAME} && docker exec {interactive_flag} {DOCKER_CONTAINER_NAME} {in_bash_commands}", quiet)


def main():
    global ONLY_SHOW_COMMAND
    os.chdir(THIS_DIR)
    if len(sys.argv) < 2:
        help()
        return

    for arg in sys.argv:
        if arg.lower() == "--show_command":
            ONLY_SHOW_COMMAND = True

    arg1 = sys.argv[1].lower()
    if arg1 == "-full_build":
        try:
            run_local_command(f"docker stop {DOCKER_CONTAINER_NAME}")
            run_local_command(f"docker rm {DOCKER_CONTAINER_NAME}")
        except subprocess.CalledProcessError:
            pass
        run_local_command(f"docker build -t {DOCKER_IMAGE_NAME} .")
        run_local_command(f"docker run --name {DOCKER_CONTAINER_NAME} -it -d -v {REPO_DIR}:{SOURCES_MOUNT_DIR} {DOCKER_IMAGE_NAME}  /bin/bash")
    elif arg1 == "-build_image":
        my_chdir(THIS_DIR)
        run_local_command(f"docker build -t {DOCKER_IMAGE_NAME} .")
    elif arg1 == "-create_container":
        run_local_command(f"docker run --name {DOCKER_CONTAINER_NAME} -it -d -v {REPO_DIR}:{SOURCES_MOUNT_DIR} {DOCKER_IMAGE_NAME}  /bin/bash")
    elif arg1 == "-recreate_container":
        try:
            run_local_command(f"docker stop {DOCKER_CONTAINER_NAME}")
            run_local_command(f"docker rm {DOCKER_CONTAINER_NAME}")
        except subprocess.CalledProcessError:
            pass
        run_local_command(f"docker run --name {DOCKER_CONTAINER_NAME} -it -d -v {REPO_DIR}:{SOURCES_MOUNT_DIR} {DOCKER_IMAGE_NAME}  /bin/bash")
    elif arg1 == "-bash":
        run_local_command(f"docker start {DOCKER_CONTAINER_NAME} && docker exec -it {DOCKER_CONTAINER_NAME} /bin/bash")
    elif arg1 == "-remove_container":
        run_local_command(f"docker stop {DOCKER_CONTAINER_NAME}")
        run_local_command(f"docker rm {DOCKER_CONTAINER_NAME}")
    elif arg1 == "-remove_image":
        run_local_command(f"docker rmi {DOCKER_IMAGE_NAME}")
    elif arg1 == "-remove_image":
        run_local_command(f"docker rmi {DOCKER_IMAGE_NAME}")
    elif arg1 == "-build_pip":
        run_docker_command("/dvp/sources/scripts/build_utilities.py run -pybind_pip_install", quiet=True, interactive=False)
    elif arg1 == "exec_it":
        bash_commands = " ".join(sys.argv[2:])
        run_docker_command(bash_commands, quiet=False, interactive=True)
    elif arg1 == "exec":
        bash_commands = " ".join(sys.argv[2:])
        run_docker_command(bash_commands, quiet=False, interactive=False)
    else:
        help()


if __name__ == "__main__":
    main()
