#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_GIT_URI="https://github.com/tianocore/edk2.git"
UPSTREAM_TAG="edk2-stable202302"
SPEC_FILE="${CURR_DIR}/ovmf.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -f ${RPMBUILD_DIR}/edk2.tar.gz ]]; then
        git clone --branch ${UPSTREAM_TAG} ${UPSTREAM_GIT_URI}
        pushd edk2
	git submodule update --init --recursive
        git apply ../0001*.patch
        popd
        tar --exclude=.git -czf "${RPMBUILD_DIR}"/SOURCES/edk2.tar.gz edk2
    fi
}

prepare() {
    echo "**** Prepare ****"
}

build() {
    echo "**** Build ****"
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

pushd "$CURR_DIR"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_origin
prepare
build
popd
