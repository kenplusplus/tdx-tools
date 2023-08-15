#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_GIT_URI="https://github.com/tianocore/edk2.git"
UPSTREAM_TAG="edk2-stable202302"

REPO_FOLDER="mvp-ovmf-stable202302"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -d ${REPO_FOLDER} ]]; then
        git clone --branch ${UPSTREAM_TAG} ${UPSTREAM_GIT_URI} ${REPO_FOLDER}
    fi

    pushd ${REPO_FOLDER}
    git submodule update --init --recursive
    popd
}

prepare() {
    echo "**** Prepare ****"
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/${REPO_FOLDER} -fr
}

build() {
    echo "**** Build ****"
    cd "${CURR_DIR}"/${REPO_FOLDER}
    echo "Patch..."
    if [[ ! -f patch.done ]]; then
	git apply ../0001*.patch
        touch patch.done
    fi
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "$CURR_DIR"
get_origin
prepare
build
popd

