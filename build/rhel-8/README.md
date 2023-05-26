
# Build TDX Stack on RHEL 8

## Build requirements

RHEL is a commercial enterprise operating system. To install packages from RHEL official repositories,
register and subscribe your system. In addition to the `BaseOS` and `Appstream` repositories, the 
`CodeReady Linux Builder` repository is required to install dependencies when building/installing TDX packages.

```
dnf install -y bzip2 coreutils cpio diffutils gcc gcc-c++ make patch unzip which \
        git wget sudo python3 python3-pyyaml python3-requests redhat-rpm-config rpm-build createrepo_c
dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
```

## Build all

Run `build-repo.sh` to build host packages into `repo/host` and guest packages into `repo/guest/`.

```
cd tdx-tools/build/rhel-8
./build-repo.sh
```

If you need to build some packages separately, go into each subdirectory and run `build.sh`.

## Install TDX host packages

Configure RHEL local repository to install the host packages.

```
sudo su
mkdir -p /srv/
mv repo/host /srv/tdx-host
cat > /etc/yum.repos.d/tdx-host-local.repo << EOL
[tdx-host-local]
name=tdx-host-local
baseurl=file:///srv/tdx-host
enabled=1
gpgcheck=0
module_hotfixes=true
EOL
dnf install intel-mvp-tdx-kernel intel-mvp-tdx-qemu-kvm intel-mvp-ovmf intel-mvp-tdx-libvirt
```
