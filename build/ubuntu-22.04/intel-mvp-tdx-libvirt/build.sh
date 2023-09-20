#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_URI="https://libvirt.org/sources/libvirt-8.6.0.tar.xz"
UPTRREAM_FILE="${UPSTREAM_URI##*/}"
PACKAGE="mvp-tdx-libvirt-v3.6"
PATCHSET="${CURR_DIR}/../../common/patches-tdx-libvirt-MVP-LIBVIRT-8.6.0-v3.6.tar.gz"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get source code..."
    if [[ ! -f ${UPTRREAM_FILE} ]]; then
        wget -O ${UPTRREAM_FILE} ${UPSTREAM_URI}
    fi
}

prepare() {
    echo "**** Prepare ****"
    if [[ ! -d ${PACKAGE} ]]; then
	mkdir ${PACKAGE}
        tar -xf ${UPTRREAM_FILE} --strip-components=1 --directory ${PACKAGE}
        cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/${PACKAGE} -fr
    fi
}

build() {
    echo "**** Build ****"
    cd ${PACKAGE}
    if [[ ! -f patch.done ]]; then
        echo "Patch..."
	tar xf ${PATCHSET}
        for p in patches/*.patch; do
           [ -f "$p" ] || break
           patch -N -p1 -i "$p"
        done
        touch patch.done
    fi
    sudo -E mk-build-deps --install --build-dep --build-indep \
        '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "${CURR_DIR}"
get_source
prepare
build
popd
