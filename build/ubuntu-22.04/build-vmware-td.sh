#!/bin/bash

set -ex
set -o pipefail

THIS_DIR=$(dirname "$(readlink -f "$0")")
VMWARE_GUEST_REPO="vmware_td_repo"
STATUS_DIR="${THIS_DIR}/build-status"
LOG_DIR="${THIS_DIR}/build-logs"

export DEBIAN_FRONTEND=noninteractive

VMWARE_GUEST_DEFAULT_PKG=" \
shim_*_amd64.deb \
grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb \
"

build_check() {
    sudo apt update

    if ! command -v "dpkg-scanpackages"
    then
        sudo apt install dpkg-dev -y
    fi

    [[ -d "$LOG_DIR" ]] || mkdir "$LOG_DIR"
    [[ -d "$STATUS_DIR" ]] || mkdir "$STATUS_DIR"
    if [[ "$1" == clean-build ]]; then
        rm -rf "${STATUS_DIR:?}"/*
    fi

    if [[ ! -z ${rust_mirror} ]]; then
        mkdir -p ~/.cargo
        cat > ~/.cargo/config << EOL
[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "${rust_mirror}"

[registries.mirror]
index = "${rust_mirror}"
EOL
    fi

    if [[ ! -z ${rustup_dist_server} ]]; then
        export RUSTUP_DIST_SERVER="${rustup_dist_server}"
    fi
    if [[ ! -z ${rustup_update_server} ]]; then
        export RUSTUP_UPDATE_SERVER="${rustup_update_server}"
    fi
}

build_shim () {
    pushd intel-mvp-tdx-guest-shim
    [[ -f $STATUS_DIR/shim.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/shim.log
    touch "$STATUS_DIR"/shim.done
    cp shim_*_amd64.deb ../$VMWARE_GUEST_REPO/more/
    popd
}

build_grub () {
    pushd intel-mvp-tdx-guest-grub2
    sudo apt remove libzfslinux-dev -y || true
    [[ -f $STATUS_DIR/grub.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/grub2.log
    touch "$STATUS_DIR"/grub.done
    cp grub-efi-*_amd64.deb  ../$VMWARE_GUEST_REPO/more/
    popd

    # Uninstall to avoid confilcts with libnvpair-dev
    sudo apt remove grub2-build-deps-depends grub2-unsigned-build-deps-depends -y || true
}

build_repo () {
    # move necessary packages to repo root directory.
    # so the local file installation keeps same as before.
    pushd $VMWARE_GUEST_REPO/more
    mv $VMWARE_GUEST_DEFAULT_PKG ../
    popd


    pushd $VMWARE_GUEST_REPO && dpkg-scanpackages . > Packages && popd
}

build_check "$1"

pushd "$THIS_DIR"
mkdir -p $VMWARE_GUEST_REPO/more

build_shim
build_grub
build_repo

popd
