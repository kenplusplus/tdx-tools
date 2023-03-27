#!/bin/bash
set -e

# Set distro related parameters according to distro
DISTRO=$(grep -w 'NAME' /etc/os-release)
if [[ "$DISTRO" =~ .*"Ubuntu".* ]]; then
    QEMU_EXEC="/usr/bin/qemu-system-x86_64"
else
    QEMU_EXEC="/usr/libexec/qemu-kvm"
fi

MIGTD="/usr/share/td-migration/migtd.bin"

usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -m <migtd file>           MigTD file
  -h                        Show this help
EOM
}

process_args() {
    while getopts "m:h" option; do
        case "${option}" in
            m) MIGTD=$OPTARG;;
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

launch_migTD() {
	$QEMU_EXEC -accel kvm \
		-M q35 \
		-cpu host,host-phys-bits,-kvm-steal-time,pmu=off \
		-smp 1,threads=1,sockets=1 \
		-m 1G \
		-object tdx-guest,id=tdx0,sept-ve-disable=off,debug=off \
		-object memory-backend-memfd-private,id=ram1,size=1G \
		-machine q35,memory-backend=ram1,confidential-guest-support=tdx0,kernel_irqchip=split \
		-bios "${MIGTD}" \
		-device vhost-vsock-pci,id=vhost-vsock-pci1,guest-cid=36,disable-legacy=on \
		-name migtd-dst,process=migtd-dst,debug-threads=on \
		-no-hpet \
		-nographic -vga none -nic none \
		-serial mon:stdio
}

process_args "$@"
launch_migTD
