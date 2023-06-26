#!/bin/bash

# SPDX-License-Identifier: MIT
#
# Run ansible-playbook within docker
#   ./docker-playbook.sh [parameters]
#
# For example:
# - Run a playbook:
#   ./docker-playbook centos-td-host.yml
# - Force rebuild the docker image
#   ./docker-playbook rebuild
#
###############################################################################

image=ansible-playbook
cwd=$(readlink -f "$(dirname "$0")")

check_user_in_docker() {
    if [[ "$(groups "$USER")" != *"docker"* ]]; then
        echo "Please add the current user $USER into docker group."
        exit 1
    fi
}

check_docker_cmd() {
    if ! command -v docker &> /dev/null; then
        echo "Please install docker first."
        exit 1
    fi
}

build_docker_image() {
    echo "Build docker image $image"
    docker build \
        --build-arg http_proxy \
        --build-arg https_proxy \
        --build-arg no_proxy \
        "$@" \
        -t $image \
        docker-ansible
}

run_docker() {
    docker run \
        -e http_proxy -e https_proxy -e no_proxy \
        -v ~/.ssh/:/home/tdxdev/host_ssh:ro \
        -v "${cwd}":/home/tdxdev/deployment \
        -v "${cwd}"/config-ansible:/etc/ansible \
        -it \
        --rm \
        $image "$@"
}

check_docker_cmd
check_user_in_docker

# if only want to build the docker image
if [[ $1 == "rebuild" ]]; then
    docker rmi $image
    build_docker_image --no-cache --force-rm
    exit
fi

# if the docker image has not been built at first time, build it
[ -n "$(docker images -q $image)" ] || build_docker_image

# Run ansible-playbook within docker
run_docker "$@"
