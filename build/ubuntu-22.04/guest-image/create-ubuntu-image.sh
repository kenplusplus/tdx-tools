#!/bin/bash
#
# Create a base Ubuntu EFI cloud guest image
#

CURR_DIR=$(dirname "$(realpath $0)")
USE_OFFICIAL_IMAGE=true
FORCE_RECREATE=false
OFFICIAL_UBUNTU_IMAGE="https://cloud-images.ubuntu.com/jammy/current/"
CLOUD_IMG="jammy-server-cloudimg-amd64.img"
GUEST_IMG="tdx-guest-ubuntu-22.04.img"
SIZE=20

ok() {
    echo -e "\e[1;32mSUCCESS: $*\e[0;0m"
}

error() {
    echo -e "\e[1;31mERROR: $*\e[0;0m"
    exit 1
}

warn() {
    echo -e "\e[1;33mWARN: $*\e[0;0m"
}

usage() {
    cat <<EOM
Usage: $(basename "$0") [OPTION]...
  -h                        Show this help
  -c                        Create customize image (not from Ubuntu official cloud image)
  -f                        Force to recreate the output image
  -s                        Specify the size of guest image
  -o <output file>          Specify the output file, default is tdx-guest-ubuntu-22.04.img
EOM
}

process_args() {
    while getopts "o:fch" option; do
        case "$option" in
        o) GUEST_IMG=$OPTARG ;;
        f) FORCE_RECREATE=true ;;
        c) USE_OFFICIAL_IMAGE=false ;;
        h)
            usage
            exit 0
            ;;
        *)
            echo "Invalid option '-$OPTARG'"
            usage
            exit 1
            ;;
        esac
    done

    if [[ "${CLOUD_IMG}" == "${GUEST_IMG}" ]]; then
        error "Please specify a different name for guest image via -o"
    fi

    if [[ -f "${GUEST_IMG}" ]]; then
        if [[ ${FORCE_RECREATE} != "true" ]]; then
            error "Guest image ${GUEST_IMG} already exist, please specify -f if want force to recreate"
            exit 1
        fi
    fi
}

download_image() {
    # Get the checksum file first
    if [[ -f ${CURR_DIR}/"SHA256SUMS" ]]; then
        rm ${CURR_DIR}/"SHA256SUMS"
    fi

    wget "${OFFICIAL_UBUNTU_IMAGE}/SHA256SUMS"

    while :; do
        # Download the cloud image if not exists
        if [[ ! -f ${CLOUD_IMG} ]]; then
            wget -O ${CURR_DIR}/${CLOUD_IMG} ${OFFICIAL_UBUNTU_IMAGE}/${CLOUD_IMG}
        fi

        # calculate the checksum
        download_sum=$(sha256sum ${CURR_DIR}/${CLOUD_IMG} | awk '{print $1}')
        found=false
        while IFS= read -r line || [[ -n "$line" ]]; do
            if [[ "$line" == *"$CLOUD_IMG"* ]]; then
                if [[ "${line%% *}" != ${download_sum} ]]; then
                    echo "Invalid download file according to sha256sum, re-download"
                    rm ${CURR_DIR}/${CLOUD_IMG}
                else
                    ok "Verify the checksum for Ubuntu cloud image."
                    return
                fi
                found=true
            fi
        done <"SHA256SUMS"
        if [[ $found != "true" ]]; then
            echo "Invalid SHA256SUM file"
            exit 1
        fi
    done
}

create_guest() {
    if [ ${USE_OFFICIAL_IMAGE} != "true" ]; then
        echo "Only support download the image from ${OFFICIAL_UBUNTU_IMAGE}"
        exit 1
    fi

    download_image

    cp ${CURR_DIR}/${CLOUD_IMG} ${CURR_DIR}/${GUEST_IMG}
    ok "Copy the ${CLOUD_IMG} => ${GUEST_IMG}"

    qemu-img resize ${GUEST_IMG} +${SIZE}G
    virt-customize \
        --run-command 'growpart /dev/sda 1' \
        --run-command 'resize2fs /dev/sda1'
}

[[ "$(command -v qemu-img)" ]] || { error "qemu-img is not installed" 1>&2 ; }

process_args "$@"
create_guest