#!/usr/bin/bash

set -e

UPSTREAM_GIT_URI="https://github.com/rhboot/shim.git"
UPSTREAM_BRANCH="shim-15.4"
DOWNSTREAM_GIT_URI="https://github.com/intel/shim-tdx.git"
DOWNSTREAM_BRANCH="tdx-shim-15.4"

CURR_DIR=$(dirname "$(readlink -f "$0")")
RPMBUILD_DIR=$CURR_DIR/rpmbuild
PATCH_SET=patches-tdx-shim-15.4
SPEC=$CURR_DIR/tdx-guest-shim.spec
REPO_DIR=shim-15.4

pushd "$CURR_DIR"
mkdir -p $PATCH_SET
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}


generate() {
    # To regenerate the sources please delete SOURCES/*.tar.gz
    if [[ -f $RPMBUILD_DIR/SOURCES/$REPO_DIR.tar.gz ]]; then
        return 0
    fi

    echo "**** Generate tdx patchset and upstream tarball ****"
    rm -rf $REPO_DIR
    git clone -b $DOWNSTREAM_BRANCH --single-branch --recurse-submodules $DOWNSTREAM_GIT_URI $REPO_DIR
    cd $REPO_DIR
    upstream_base=$(git ls-remote $UPSTREAM_GIT_URI refs/heads/$UPSTREAM_BRANCH | cut -f 1)
    git format-patch "$upstream_base"..$DOWNSTREAM_BRANCH
    git checkout "$upstream_base"
    cd ..
    mv $REPO_DIR/*.patch $PATCH_SET/
    tar --exclude=.git --exclude=.gitignore -czf "$RPMBUILD_DIR"/SOURCES/$REPO_DIR.tar.gz $REPO_DIR
}

prepare() {
    echo "**** Will apply all patches put in $PATCH_SET ****"
    tar cvf $PATCH_SET.tar.gz -C $PATCH_SET .
    mv "$CURR_DIR"/$PATCH_SET.tar.gz "$RPMBUILD_DIR"/SOURCES/
}

build() {
    echo "**** Install dependencies and build RPM packages ****"
    sudo -E dnf builddep --define "_topdir $RPMBUILD_DIR" -y "$SPEC"
    rpmbuild --define "_topdir $RPMBUILD_DIR" --undefine=_disable_source_fetch -v -ba "$SPEC"
}

generate
prepare
build

popd
