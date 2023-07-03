#!/bin/bash

set -e


CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_URI="https://libvirt.org/sources/libvirt-8.6.0.tar.xz"
UPTRREAM_FILE="${UPSTREAM_URI##*/}"
PATCHSET="${CURR_DIR}/../../common/patches-tdx-libvirt-MVP-LIBVIRT-8.6.0-v2.6.tar.gz"

SPEC_FILE="${CURR_DIR}/tdx-libvirt.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

get_source() {
    echo "**** Download origin package ****"
    if [[ ! -f "${RPMBUILD_DIR}"/SOURCES/"${UPTRREAM_FILE}" ]]; then
        wget -O "${UPTRREAM_FILE}" ${UPSTREAM_URI}
    fi
}

prepare() {
    echo "**** Prepare ****"
    
    cp "${UPTRREAM_FILE}" "${RPMBUILD_DIR}"/SOURCES/
    cp "${PATCHSET}" "${RPMBUILD_DIR}"/SOURCES/
}

build() {
    echo "**** Build ****"
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

pushd "${CURR_DIR}"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_source
prepare
build
popd
