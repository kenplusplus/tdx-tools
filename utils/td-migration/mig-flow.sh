#!/bin/bash
set -e

DEST_IP="localhost"
INCOMING_PORT=6666


usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i                        Destination platform ip, default is "localhost"
  -p                        incoming port
  -h                        Show this help
EOM
}

process_args() {
    while getopts "i:p:h" option; do
        case "${option}" in
            i) DEST_IP=$OPTARG;;
            p) INCOMING_PORT=$OPTARG;;
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
}

migrate() {
    echo "migrate_set_parameter max-bandwidth 100G" | nc -U /tmp/qmp-sock-src
    echo "migrate -d tcp:${DEST_IP}:${INCOMING_PORT}" | nc -U /tmp/qmp-sock-src
}

process_args "$@"
migrate