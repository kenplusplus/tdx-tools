#!/bin/bash

set -ex

UPSTREAM_GIT_URI="https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
UPSTREAM_TAG="v6.2.16"

CURR_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR="${CURR_DIR}/mvp-tdx-kernel-${UPSTREAM_TAG}"
PATCHSET="${CURR_DIR}/../../common/patches-tdx-kernel-MVP-KERNEL-6.2.16-v3.7.tar.gz"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get upstream source code..."
    cd "${CURR_DIR}"
    if [[ ! -d ${SOURCE_DIR} ]]; then
        git clone  -b ${UPSTREAM_TAG} --single-branch --depth 1 ${UPSTREAM_GIT_URI} "${SOURCE_DIR}"
        tar xf "${PATCHSET}"

        cd "${SOURCE_DIR}"
        git config user.name "${USER:-tdx-builder}"
        git config user.email "${USER:-tdx-builder}"@"${HOSTNAME}"
        for i in ../patches/*; do
            git am "$i"
        done
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/debian/ "${SOURCE_DIR}" -fr
    cp "${CURR_DIR}"/debian.master/ "${SOURCE_DIR}" -fr
    cp "${CURR_DIR}"/linux-6.2.16/* "${SOURCE_DIR}" -fr

    sudo apt update
    if [[ -f /etc/timezone ]]; then
        sudo DEBIAN_FRONTEND=noninteractive apt install tzdata -y
    else
        sudo DEBIAN_FRONTEND=noninteractive TZ=America/New_York apt install tzdata -y
    fi
}

build() {
    echo "Build..."
    cd "${SOURCE_DIR}"
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
