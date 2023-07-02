#!/bin/bash
set -e

TYPE="local"
DEST_IP=""
VSOCK_PORT_SRC=1234
VSOCK_PORT_DST=1235

usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i <dest ip>              Destination platform ip address
  -t <local|remote>         Use single or cross host live migration
  -s <source port>          Source port
  -d <destination port>     Destination port
  -h                        Show this help
EOM
}

process_args() {
    while getopts "i:t:s:d:h" option; do
        case "${option}" in
            i) DEST_IP=$OPTARG;;
            t) TYPE=$OPTARG;;
            s) VSOCK_PORT_SRC=$OPTARG;;
            d) VSOCK_PORT_DST=$OPTARG;;
            h) usage
               exit 0
               ;;
            *)
               echo "Invalid option '-$OPTARG'"
               usage
               exit 1
               ;;
        esac
    done

    case ${TYPE} in
        "local");;
        "remote")
            if [[ -z ${DEST_IP} ]]; then
                error "Please use -i specify DEST_IP in remote type"
            fi
            ;;
        *)
            error "Invalid ${TYPE}, must be [local|remote]"
            ;;
    esac
}

error() {
    echo -e "\e[1;31mERROR: $*\e[0;0m"
    exit 1
}

pre_mig(){
    # Asking migtd-dst to connect to the dst socat
    if [[ ${TYPE} == "local" ]]; then
        echo "qom-set /objects/tdx0/ vsockport ${VSOCK_PORT_DST}" | nc -U /tmp/qmp-sock-dst -w3
    else 
       ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo qom-set /objects/tdx0/ vsockport ${VSOCK_PORT_DST} | nc -U /tmp/qmp-sock-dst"
    fi

    # Asking migtd-dst to connect to the src socat
    echo "qom-set /objects/tdx0/ vsockport ${VSOCK_PORT_SRC}" | nc -U /tmp/qmp-sock-src -w3
}

process_args "$@"
pre_mig
