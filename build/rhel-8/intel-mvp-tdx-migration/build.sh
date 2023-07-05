#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
RPMBUILD_DIR=${CURR_DIR}/rpmbuild
SPEC_FILE="${CURR_DIR}/tdx-migration.spec"
GIT_URI="https://github.com/intel/MigTD.git"
GIT_TAG="v0.2.3"
PKG_DIR="${CURR_DIR}"/migtd

get_source() {
    echo "Get upstream source code..."

    cd "${CURR_DIR}"
    if [[ ! -d ${PKG_DIR} ]]; then
        git clone --single-branch --branch ${GIT_TAG} ${GIT_URI} "${PKG_DIR}"
        pushd "${PKG_DIR}"
        git submodule update --init --recursive
        popd
    fi

    tar czf "${RPMBUILD_DIR}"/SOURCES/tdx-migration.tar.gz migtd
}

prepare() {
    echo "Prepare..."
}

build() {
    echo "Build..."
    sudo dnf groupinstall -y 'Development Tools'
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_source
prepare
build
