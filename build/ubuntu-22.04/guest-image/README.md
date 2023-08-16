# Ubuntu 22.04 TDX Guest Image

Customize Ubuntu 22.04 cloud image and install TDX guest kernel.

## Prerequisites

- The script will install TDX guest packages from `../guest_repo/`. If not present, please build the guest repo in the upper build directory:

`./pkg-builder build-repo.sh guest`

- Install qemu-img and virt-customize. For Ubuntu:

`sudo apt install -y qemu-utils libguestfs-tools`

## Steps

- Run the script to generate `td-guest-ubuntu-22.04.qcow2`. The login credential for the guest is `root/123456`.

`./tdx-guest-stack.sh`
