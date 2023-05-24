#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")

GIT_URI="https://github.com/intel/amber-client.git"
GIT_TAG="2023ww21"
REPO_FOLDER="amber-cli"

get_source() {
    echo "Get source code..."

    cd "${CURR_DIR}"
    if [[ ! -d ${REPO_FOLDER} ]]; then
        git clone --single-branch --branch ${GIT_TAG} ${GIT_URI} ${REPO_FOLDER}
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}/${REPO_FOLDER}/" -fr

    # Github runner overrides to /github/home
    user_id=$(id -u)
    if [ "$user_id" -eq 0 ]; then
        export HOME=/root
    fi

    # tdx_attest library
    if [[ ! -d sgx_debian_local_repo ]]; then
        wget https://download.01.org/intel-sgx/sgx-dcap/1.16/linux/distro/ubuntu22.04-server/sgx_debian_local_repo.tgz
        tar xf sgx_debian_local_repo.tgz
    fi
    sudo apt install ./sgx_debian_local_repo/pool/main/libt/libtdx-attest/libtdx-attest-dev_1.16.100.2-jammy1_amd64.deb \
        ./sgx_debian_local_repo/pool/main/libt/libtdx-attest/libtdx-attest_1.16.100.2-jammy1_amd64.deb -y
}

build() {
    echo "Build..."
    cd "${CURR_DIR}/${REPO_FOLDER}/"

    dpkg-source --before-build .
    sudo mk-build-deps -i -r -t "apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y"
    make -C amber-cli-tdx cli
    debuild -uc -us -b
}

get_source
prepare
build
