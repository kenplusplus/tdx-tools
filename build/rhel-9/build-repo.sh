#!/bin/bash

set -e
set -o pipefail

THIS_DIR=$(dirname "$(readlink -f "$0")")
STATUS_DIR="${THIS_DIR}/build-status"
LOG_DIR="${THIS_DIR}/build-logs"

PACKAGES_GUEST=( \
    intel-mvp-tdx-kernel \
    )

PACKAGES_HOST=( \
    intel-mvp-tdx-kernel \
    intel-mvp-tdx-qemu-kvm \
    intel-mvp-tdx-libvirt \
    intel-mvp-ovmf \
    intel-mvp-tdx-migration \
    intel-mvp-vtpm-td \
    )

build_repo() {
    packages=("${@:2}")
    repo_type=$1
    mkdir -p "${THIS_DIR}"/repo/"${repo_type}"/src

    for package in "${packages[@]}"; do
        pushd "${THIS_DIR}"/"${package}" || exit 1
        if [[ ! -f "$STATUS_DIR/build-${package}.done" ]]; then
            ./build.sh 2>&1 | tee "$LOG_DIR/build-${package}.log"
            touch "$STATUS_DIR/build-${package}.done"
        fi
        cp ./rpmbuild/RPMS/* ../repo/"${repo_type}"/ -fr
        cp ./rpmbuild/SRPMS/* ../repo/"${repo_type}"/src -fr
        popd || exit 1
    done
}

finalize() {
    repo_type=$1
    echo "Create $repo_type repo"
    pushd "${THIS_DIR}"/repo/"${repo_type}" || exit 1
    createrepo .
    popd || exit 1
}

# Check whether distro is el9
[[ $(< /etc/os-release) =~ "platform:el9" ]] || { echo "Invalid OS" && exit 1; }

# Check whether createrepo tool installed
if ! command -v "createrepo"
then
    sudo dnf install createrepo_c -y
fi

[[ -d "$LOG_DIR" ]] || mkdir "$LOG_DIR"
[[ -d "$STATUS_DIR" ]] || mkdir "$STATUS_DIR"
if [[ "$1" == clean-build ]]; then
    rm -rf "${STATUS_DIR:?}"/*
fi

# Build host repo
build_repo "host" "${PACKAGES_HOST[@]}"

# Build guest repo
build_repo "guest" "${PACKAGES_GUEST[@]}"

# Finalize
finalize "host"
finalize "guest"
