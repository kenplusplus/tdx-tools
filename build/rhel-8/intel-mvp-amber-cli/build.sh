#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")

GIT_URI="https://github.com/intel/amber-client.git"
GIT_TAG="2023ww21"
SPEC_FILE="${CURR_DIR}"/amber-cli.spec
RPMBUILD_DIR="${CURR_DIR}"/rpmbuild
REPO_FOLDER="amber-cli"

get_source() {
    echo "Get source code..."

    cd "${CURR_DIR}"
    if [[ ! -d ${REPO_FOLDER} ]]; then
        git clone --single-branch --branch ${GIT_TAG} ${GIT_URI} ${REPO_FOLDER}
    fi
    tar czf "${RPMBUILD_DIR}"/SOURCES/${REPO_FOLDER}.tar.gz ${REPO_FOLDER}
}

prepare() {
    echo "Prepare..."

    # Github runner overrides to /github/home
    user_id=$(id -u)
    if [ "$user_id" -eq 0 ]; then
        export HOME=/root
    fi

    # tdx_attest library
    if [[ ! -d sgx_rpm_local_repo ]]; then
        wget https://download.01.org/intel-sgx/sgx-dcap/1.17/linux/distro/rhel8.6-server/sgx_rpm_local_repo.tgz
        tar xf sgx_rpm_local_repo.tgz
    fi
    sudo dnf install sgx_rpm_local_repo/libtdx-attest-1.17.100.4-1.el8.x86_64.rpm \
        sgx_rpm_local_repo/libtdx-attest-devel-1.17.100.4-1.el8.x86_64.rpm -y
}

build() {
    echo "Build..."
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_source
prepare
build
