#!/bin/bash

set -ex

CURR_DIR="$(dirname "$(readlink -f "$0")")"

UPSTREAM_GIT_URI="https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
UPSTREAM_TAG="v6.2.16"

PATCHSET="${CURR_DIR}/../../common/patches-tdx-kernel-MVP-KERNEL-6.2.16-v5.0.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-kernel.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

prepare() {
    echo "Prepare..."

    if [[ ! -f "${RPMBUILD_DIR}/SOURCES/linux-tdx-kernel.tar.gz" ]]; then
        if [[ ! -d linux-tdx-kernel ]]; then
            git clone -b ${UPSTREAM_TAG} --single-branch --depth 1 ${UPSTREAM_GIT_URI} linux-tdx-kernel
            tar xf "${PATCHSET}"
            cd linux-tdx-kernel
            git config user.name "${USER:-tdx-builder}"
            git config user.email "${USER:-tdx-builder}"@"$HOSTNAME"
            for i in ../patches/*; do
                git am "$i"
            done
            cd -
        fi
        tar --exclude=.git -czf linux-tdx-kernel.tar.gz linux-tdx-kernel
        mv linux-tdx-kernel.tar.gz "${RPMBUILD_DIR}"/SOURCES/
    fi

    cp "${CURR_DIR}"/*.config "${RPMBUILD_DIR}"/SOURCES/
}

build() {
    echo "Build..."
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" --undefine=_disable_source_fetch -v -ba "${SPEC_FILE}" --with baseonly --without kabichk
}

pushd "${CURR_DIR}"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
prepare
build
popd
