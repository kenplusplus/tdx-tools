#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_VERSION="7.0.50"
UPSTREAM_GIT_URI="https://github.com/qemu/qemu.git"
UPSTREAM_TAG="ad4c7f529a279685da84297773b4ec8080153c2d"
PACKAGE="mvp-tdx-qemu-${UPSTREAM_VERSION}"
PATCHSET="${CURR_DIR}/../../common/patches-tdx-qemu-MVP-QEMU-7.0-v2.1.tar.gz"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get downstream source code..."
    if [[ ! -d ${PACKAGE} ]]; then
        git clone ${UPSTREAM_GIT_URI} ${PACKAGE}
        cd ${PACKAGE}
        tar xf "${PATCHSET}"
        git checkout ${UPSTREAM_TAG}
        git config user.name "${USER:-tdx-builder}"
        git config user.email "${USER:-tdx-builder}"@"$HOSTNAME"
        for i in patches/*; do
           git am "$i"
        done
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/"${PACKAGE}" -fr

    sudo apt update
    sudo apt install systemd libcapstone-dev -y
    if [[ -f /etc/timezone ]]; then
        sudo DEBIAN_FRONTEND=noninteractive apt install tzdata -y
    else
        sudo DEBIAN_FRONTEND=noninteractive TZ=America/New_York apt install tzdata -y
    fi
}

build() {
    echo "Build..."
    cd "${CURR_DIR}"/${PACKAGE}
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "${CURR_DIR}"
get_source
prepare
build
popd
