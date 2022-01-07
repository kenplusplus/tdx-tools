#!/bin/bash

echo $PWD
echo $0
echo $1
ls $PWD

env
PACKAGE_ROOT="$PWD/build/centos-stream-8"

echo $PACKAGE_ROOT

if [[ ! -d "${PACKAGE_ROOT}/${INPUT_PACKAGE}" ]]; then
    echo "Invalid package: ${INPUT_PACKAGE}"
    exit 1
fi

cd "${PACKAGE_ROOT}/${INPUT_PACKAGE}"
./build.sh
