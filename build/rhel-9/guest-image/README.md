# REHL 9.2 TDX Guest Image

Create a TDX guest image in EFI schema, with customized packages.

## Prerequisites

- RHEL 9.2 base ISO image. You can download it from https://access.redhat.com/downloads. 

- virt-manager and libvirt. Please install them via `sudo dnf install -y virt-manager libguestfs-tools-c` .

## Steps

- Prepare a tdx guest repo `GUEST_REPO` in local, containing kernels.

- Provide a RHEL iso `GUEST_ISO`

- Provide software repos in script `./cloud-init-data/init-scripts/add_repos.sh` to provide packages grub2-efi-x64 and shim-x64.

- Create a guest image

Build a guest image named by `$GUEST_NAME`, from the iso file `$GUEST_ISO`, installing TDX kernel from repo `$GUEST_REPO`. 

`./create-redhat-image.sh -l $GUEST_ISO -r $GUEST_REPO -o $GUEST_NAME`

It will create a clear qcow file named by `$GUEST_NAME` in the current directory and a qcow guest with TDX enabling in `/tmp/$GUEST_NAME`.

If you already have a qcow2 image `GUEST_QCOW2`, you can build a guest image from it directly.

`./create-redhat-image.sh -q $GUEST_QCOW2 -r $GUEST_REPO -o $GUEST_NAME`

