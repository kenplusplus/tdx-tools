# -*- rpm-spec -*-

# This spec file assumes you are building on a Fedora or RHEL version
# that's still supported by the vendor. It may work on other distros
# or versions, but no effort will be made to ensure that going forward.
%define min_rhel 8
%define min_fedora 33

%define arches_qemu_kvm         %{ix86} x86_64 %{power64} %{arm} aarch64 s390x
%if 0%{?rhel}
    %if 0%{?rhel} > 8
        %define arches_qemu_kvm     x86_64 aarch64 s390x
    %else
        %define arches_qemu_kvm     x86_64 %{power64} aarch64 s390x
    %endif
%endif

%define arches_64bit            x86_64 %{power64} aarch64 s390x riscv64
%define arches_x86              %{ix86} x86_64

%define arches_systemtap_64bit  %{arches_64bit}
%define arches_dmidecode        %{arches_x86}
%define arches_xen              %{arches_x86} aarch64
%if 0%{?fedora} >= 36
    %define arches_xen              x86_64 aarch64
%endif
%define arches_vbox             %{arches_x86}
%define arches_ceph             %{arches_64bit}
%define arches_zfs              %{arches_x86} %{power64} %{arm}
%define arches_numactl          %{arches_x86} %{power64} aarch64 s390x
%define arches_numad            %{arches_x86} %{power64} aarch64

# The hypervisor drivers that run in libvirtd
%define with_qemu          0%{!?_without_qemu:1}
%define with_lxc           0%{!?_without_lxc:1}
%define with_libxl         0%{!?_without_libxl:1}
%define with_vbox          0%{!?_without_vbox:1}

%ifarch %{arches_qemu_kvm}
    %define with_qemu_kvm      %{with_qemu}
%else
    %define with_qemu_kvm      0
%endif

%define with_qemu_tcg      %{with_qemu}

# RHEL disables TCG on all architectures
%if 0%{?rhel}
    %define with_qemu_tcg 0
%endif

%if ! %{with_qemu_tcg} && ! %{with_qemu_kvm}
    %define with_qemu 0
%endif

# Then the hypervisor drivers that run outside libvirtd, in libvirt.so
%define with_openvz        0%{!?_without_openvz:1}
%define with_vmware        0%{!?_without_vmware:1}
%define with_esx           0%{!?_without_esx:1}
%define with_hyperv        0%{!?_without_hyperv:1}

# Then the secondary host drivers, which run inside libvirtd
%define with_storage_rbd      0%{!?_without_storage_rbd:1}

%if 0%{?fedora}
    %define with_storage_sheepdog 0%{!?_without_storage_sheepdog:1}
%else
    %define with_storage_sheepdog 0
%endif

%define with_storage_gluster 0%{!?_without_storage_gluster:1}
%if 0%{?rhel}
    # Glusterfs has been dropped in RHEL-9, and before that
    # was only enabled on arches where KVM exists
    %if 0%{?rhel} > 8
        %define with_storage_gluster 0
    %else
        %ifnarch %{arches_qemu_kvm}
            %define with_storage_gluster 0
        %endif
    %endif
%endif

# Fedora has zfs-fuse
%if 0%{?fedora}
    %define with_storage_zfs      0%{!?_without_storage_zfs:1}
%else
    %define with_storage_zfs      0
%endif

%define with_storage_iscsi_direct 0%{!?_without_storage_iscsi_direct:1}
# libiscsi has been dropped in RHEL-9
%if 0%{?rhel} > 8
    %define with_storage_iscsi_direct 0
%endif

# Other optional features
%define with_numactl          0%{!?_without_numactl:1}

# A few optional bits off by default, we enable later
%define with_fuse             0
%define with_sanlock          0
%define with_numad            0
%define with_firewalld_zone   0
%define with_netcf            0
%define with_libssh2          0
%define with_wireshark        0
%define with_libssh           0
%define with_dmidecode        0

# Finally set the OS / architecture specific special cases

# Architecture-dependent features
%ifnarch %{arches_xen}
    %define with_libxl 0
%endif
%ifnarch %{arches_vbox}
    %define with_vbox 0
%endif
%ifnarch %{arches_numactl}
    %define with_numactl 0
%endif
%ifnarch %{arches_zfs}
    %define with_storage_zfs 0
%endif
%ifnarch %{arches_ceph}
    %define with_storage_rbd 0
%endif

# RHEL doesn't ship many hypervisor drivers
%if 0%{?rhel}
    %define with_openvz 0
    %define with_vbox 0
    %define with_vmware 0
    %define with_libxl 0
    %define with_hyperv 0
    %define with_vz 0
    %define with_lxc 0
%endif

%define with_firewalld_zone 0%{!?_without_firewalld_zone:1}

%if (0%{?fedora} && 0%{?fedora} < 34) || (0%{?rhel} && 0%{?rhel} < 9)
    %define with_netcf 0%{!?_without_netcf:1}
%endif

# fuse is used to provide virtualized /proc for LXC
%if %{with_lxc}
    %define with_fuse      0%{!?_without_fuse:1}
%endif

# Enable sanlock library for lock management with QEMU
# Sanlock is available only on arches where kvm is available for RHEL
%if 0%{?fedora}
    %define with_sanlock 0%{!?_without_sanlock:1}
%endif
%if 0%{?rhel}
    %ifarch %{arches_qemu_kvm}
        %define with_sanlock 0%{!?_without_sanlock:1}
    %endif
%endif

# Enable libssh2 transport for new enough distros
%if 0%{?fedora}
    %define with_libssh2 0%{!?_without_libssh2:1}
%endif

# Enable wireshark plugins for all distros
%define with_wireshark 0%{!?_without_wireshark:1}
%define wireshark_plugindir %(pkg-config --variable plugindir wireshark)/epan

# Enable libssh transport for all distros
%define with_libssh 0%{!?_without_libssh:1}

%if %{with_qemu} || %{with_lxc}
# numad is used to manage the CPU and memory placement dynamically,
# it's not available on many non-x86 architectures.
    %ifarch %{arches_numad}
        %define with_numad    0%{!?_without_numad:1}
    %endif
%endif

%ifarch %{arches_dmidecode}
    %define with_dmidecode 0%{!?_without_dmidecode:1}
%endif

%define with_modular_daemons 0
%if 0%{?fedora} >= 35 || 0%{?rhel} >= 9
    %define with_modular_daemons 1
%endif

# Force QEMU to run as non-root
%define qemu_user  qemu
%define qemu_group  qemu

# Locations for QEMU data
%define qemu_moddir %{_libdir}/qemu
%define qemu_datadir %{_datadir}/qemu

%define with_mingw 0
%if 0%{?fedora}
    %define with_mingw 0%{!?_without_mingw:1}
%endif

# RHEL releases provide stable tool chains and so it is safe to turn
# compiler warning into errors without being worried about frequent
# changes in reported warnings
%if 0%{?rhel}
    %define enable_werror -Dwerror=true
%else
    %define enable_werror -Dwerror=false -Dgit_werror=disabled
%endif

%define enable_werror -Dwerror=false

%define tls_priority "@LIBVIRT,SYSTEM"

# libvirt 8.1.0 stops distributing any sysconfig files.
# If the user has customized their sysconfig file,
# the RPM upgrade path will rename it to .rpmsave
# because the file is no longer managed by RPM.
# To prevent a regression we rename it back after the
# transaction to preserve the user's modifications
%define libvirt_sysconfig_pre() \
    for sc in %{?*} ; do \
        test -f "%{_sysconfdir}/sysconfig/${sc}.rpmsave" || continue ; \
        mv -v "%{_sysconfdir}/sysconfig/${sc}.rpmsave" "%{_sysconfdir}/sysconfig/${sc}.rpmsave.old" ; \
    done \
    %{nil}
%define libvirt_sysconfig_posttrans() \
    for sc in %{?*} ; do \
        test -f "%{_sysconfdir}/sysconfig/${sc}.rpmsave" || continue ; \
        mv -v "%{_sysconfdir}/sysconfig/${sc}.rpmsave" "%{_sysconfdir}/sysconfig/${sc}" ; \
    done \
    %{nil}

Summary: Library providing a simple virtualization API
Name: libvirt
Version: 8.6.0
%define patch_number 16
%define downstream_tag MVP-LIBVIRT-8.6.0-v3.6
Release: v3.6.mvp%{patch_number}%{?dist}
License: LGPLv2+
URL: https://libvirt.org/

Epoch: 23

%if %(echo %{version} | grep -q "\.0$"; echo $?) == 1
    %define mainturl stable_updates/
%endif
Source: libvirt-%{version}.tar.xz
Source1: patches-tdx-libvirt-%{downstream_tag}.tar.gz
Source2: https://git.centos.org/rpms/libvirt/raw/e8e641e161b26dd08227d56054946449e9a1a437/f/SOURCES/symlinks

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-config-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-config-nwfilter = %{epoch}:%{version}-%{release}
%if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{epoch}:%{version}-%{release}
%endif
%if %{with_lxc}
Requires: libvirt-daemon-driver-lxc = %{epoch}:%{version}-%{release}
%endif
%if %{with_qemu}
Requires: libvirt-daemon-driver-qemu = %{epoch}:%{version}-%{release}
%endif
# We had UML driver, but we've removed it.
Obsoletes: libvirt-daemon-driver-uml <= 5.0.0
Obsoletes: libvirt-daemon-uml <= 5.0.0
%if %{with_vbox}
Requires: libvirt-daemon-driver-vbox = %{epoch}:%{version}-%{release}
%endif
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{epoch}:%{version}-%{release}
Requires: libvirt-client = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

# All build-time requirements. Run-time requirements are
# listed against each sub-RPM
BuildRequires: python3-docutils
BuildRequires: gcc
BuildRequires: meson >= 0.56.0
BuildRequires: ninja-build
BuildRequires: git
BuildRequires: perl-interpreter
BuildRequires: python3
%if %{with_libxl}
BuildRequires: xen-devel
%endif
BuildRequires: glib2-devel >= 2.56
BuildRequires: libxml2-devel
BuildRequires: libxslt
BuildRequires: readline-devel
BuildRequires: bash-completion >= 2.0
BuildRequires: gettext
BuildRequires: libtasn1-devel
BuildRequires: gnutls-devel
BuildRequires: libattr-devel
# For pool-build probing for existing pools
BuildRequires: libblkid-devel >= 2.17
# for augparse, optionally used in testing
BuildRequires: augeas
BuildRequires: systemd-devel >= 185
BuildRequires: systemd-rpm-macros
BuildRequires: libpciaccess-devel >= 0.10.9
BuildRequires: yajl-devel
%if %{with_sanlock}
BuildRequires: sanlock-devel >= 2.4
%endif
BuildRequires: libpcap-devel >= 1.5.0
BuildRequires: libnl3-devel
BuildRequires: libselinux-devel
BuildRequires: iptables
BuildRequires: ebtables
BuildRequires: module-init-tools
BuildRequires: cyrus-sasl-devel
BuildRequires: polkit >= 0.112
# For mount/umount in FS driver
BuildRequires: util-linux
%if %{with_qemu}
# For managing ACLs
BuildRequires: libacl-devel
# From QEMU RPMs
BuildRequires: /usr/bin/qemu-img
%endif
# For LVM drivers
BuildRequires: lvm2
# For pool type=iscsi
BuildRequires: iscsi-initiator-utils
%if %{with_storage_iscsi_direct}
# For pool type=iscsi-direct
BuildRequires: libiscsi-devel
%endif
# For disk driver
BuildRequires: parted-devel
# For Multipath support
BuildRequires: device-mapper-devel
%if %{with_storage_rbd}
BuildRequires: librados-devel
BuildRequires: librbd-devel
%endif
%if %{with_storage_gluster}
BuildRequires: glusterfs-api-devel >= 3.4.1
BuildRequires: glusterfs-devel >= 3.4.1
%endif
%if %{with_numactl}
# For QEMU/LXC numa info
BuildRequires: numactl-devel
%endif
BuildRequires: libcap-ng-devel >= 0.5.0
%if %{with_fuse}
BuildRequires: fuse-devel >= 2.8.6
%endif
%if %{with_libssh2}
BuildRequires: libssh2-devel >= 1.3.0
%endif
%if %{with_netcf}
BuildRequires: netcf-devel >= 0.2.2
%endif
%if (0%{?fedora} >= 36) || (0%{?rhel} >= 9)
BuildRequires: passt
%endif
%if %{with_esx}
BuildRequires: libcurl-devel
%endif
%if %{with_hyperv}
BuildRequires: libwsman-devel >= 2.6.3
%endif
BuildRequires: audit-libs-devel
# we need /usr/sbin/dtrace
BuildRequires: systemtap-sdt-devel
# For mount/umount in FS driver
BuildRequires: util-linux
# For showmount in FS driver (netfs discovery)
BuildRequires: nfs-utils
# Fedora build root suckage
BuildRequires: gawk
# For storage wiping with different algorithms
BuildRequires: scrub
%if %{with_numad}
BuildRequires: numad
%endif
%if %{with_wireshark}
BuildRequires: wireshark-devel
%endif
%if %{with_libssh}
BuildRequires: libssh-devel >= 0.8.1
%endif
BuildRequires: rpcgen
BuildRequires: libtirpc-devel
# Needed for the firewalld_reload macro
%if %{with_firewalld_zone}
BuildRequires: firewalld-filesystem
%endif

%if %{with_mingw}
BuildRequires: mingw32-filesystem
BuildRequires: mingw32-gcc
BuildRequires: mingw32-binutils
BuildRequires: mingw32-glib2 >= 2.48
BuildRequires: mingw32-libgpg-error
BuildRequires: mingw32-libgcrypt
BuildRequires: mingw32-gnutls
BuildRequires: mingw32-gettext
BuildRequires: mingw32-libxml2
BuildRequires: mingw32-portablexdr
BuildRequires: mingw32-dlfcn
BuildRequires: mingw32-libssh2
BuildRequires: mingw32-curl
BuildRequires: mingw64-filesystem
BuildRequires: mingw64-gcc
BuildRequires: mingw64-binutils
BuildRequires: mingw64-glib2 >= 2.48
BuildRequires: mingw64-libgpg-error
BuildRequires: mingw64-libgcrypt
BuildRequires: mingw64-gnutls
BuildRequires: mingw64-gettext
BuildRequires: mingw64-libxml2
BuildRequires: mingw64-portablexdr
BuildRequires: mingw64-dlfcn
BuildRequires: mingw64-libssh2
BuildRequires: mingw64-curl
%endif

%description
Libvirt is a C toolkit to interact with the virtualization capabilities
of recent versions of Linux (and other OSes). The main package includes
the libvirtd server exporting the virtualization support.

%package docs
Summary: API reference and website documentation

%description docs
Includes the API reference for the libvirt C library, and a complete
copy of the libvirt.org website documentation.

%package daemon
Summary: Server side daemon and supporting files for libvirt library

# All runtime requirements for the libvirt package (runtime requrements
# for subpackages are listed later in those subpackages)

# The client side, i.e. shared libs are in a subpackage
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
# The libvirt-guests.sh script requires virsh from libvirt-client subpackage,
# but not every deployment wants to use libvirt-guests service. Using
# Recommends here will install libvirt-client by default (if available), but
# RPM won't complain if the package is unavailable, masked, or removed later.
Recommends: libvirt-client = %{epoch}:%{version}-%{release}
# netcat is needed on the server side so that clients that have
# libvirt < 6.9.0 can connect, but newer versions will prefer
# virt-ssh-helper. Making this a Recommends means that it gets
# installed by default, but can still be removed if compatibility
# with old clients is not required
Recommends: /usr/bin/nc
# for modprobe of pci devices
Requires: module-init-tools
# for /sbin/ip
Requires: iproute
# for /sbin/tc
Requires: iproute-tc
Requires: polkit >= 0.112
%if %{with_dmidecode}
# For virConnectGetSysinfo
Requires: dmidecode
%endif
# For service management
Requires(post): /usr/bin/systemctl
%if %{with_numad}
Requires: numad
%endif
# libvirtd depends on 'messagebus' service
Requires: dbus
# For uid creation during pre
Requires(pre): shadow-utils
# Needed by /usr/libexec/libvirt-guests.sh script.
%if 0%{?fedora} >= 37
Requires: gettext-runtime
%else
Requires: gettext
%endif

# Ensure smooth upgrades
Obsoletes: libvirt-admin < 7.3.0
Provides: libvirt-admin = %{epoch}:%{version}-%{release}
Obsoletes: libvirt-bash-completion < 7.3.0

%description daemon
Server side daemon required to manage the virtualization capabilities
of recent versions of Linux. Requires a hypervisor specific sub-RPM
for specific drivers.

%package daemon-config-network
Summary: Default configuration files for the libvirtd daemon

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}

%description daemon-config-network
Default configuration files for setting up NAT based networking

%package daemon-config-nwfilter
Summary: Network filter configuration files for the libvirtd daemon

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}

%description daemon-config-nwfilter
Network filter configuration files for cleaning guest traffic

%package daemon-driver-network
Summary: Network driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: dnsmasq >= 2.41
Requires: iptables

%description daemon-driver-network
The network driver plugin for the libvirtd daemon, providing
an implementation of the virtual network APIs using the Linux
bridge capabilities.

%package daemon-driver-nwfilter
Summary: Nwfilter driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: iptables
Requires: ebtables

%description daemon-driver-nwfilter
The nwfilter driver plugin for the libvirtd daemon, providing
an implementation of the firewall APIs using the ebtables,
iptables and ip6tables capabilities

%package daemon-driver-nodedev
Summary: Nodedev driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
# needed for device enumeration
Requires: systemd >= 185
# For managing persistent mediated devices
Requires: mdevctl

%description daemon-driver-nodedev
The nodedev driver plugin for the libvirtd daemon, providing
an implementation of the node device APIs using the udev
capabilities.

%package daemon-driver-interface
Summary: Interface driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
%if %{with_netcf}
Requires: netcf-libs >= 0.2.2
%endif

%description daemon-driver-interface
The interface driver plugin for the libvirtd daemon, providing
an implementation of the host network interface APIs.

%package daemon-driver-secret
Summary: Secret driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description daemon-driver-secret
The secret driver plugin for the libvirtd daemon, providing
an implementation of the secret key APIs.

%package daemon-driver-storage-core
Summary: Storage driver plugin including base backends for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: nfs-utils
# For mkfs
Requires: util-linux
%if %{with_qemu}
# From QEMU RPMs
Requires: /usr/bin/qemu-img
%endif
%if !%{with_storage_rbd}
Obsoletes: libvirt-daemon-driver-storage-rbd < 5.2.0
%endif
Obsoletes: libvirt-daemon-driver-storage-sheepdog < 8.8.0

%description daemon-driver-storage-core
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using files, local disks, LVM, SCSI,
iSCSI, and multipath storage.

%package daemon-driver-storage-logical
Summary: Storage driver plugin for lvm volumes
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: lvm2

%description daemon-driver-storage-logical
The storage driver backend adding implementation of the storage APIs for block
volumes using lvm.

%package daemon-driver-storage-disk
Summary: Storage driver plugin for disk
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: parted
Requires: device-mapper

%description daemon-driver-storage-disk
The storage driver backend adding implementation of the storage APIs for block
volumes using the host disks.

%package daemon-driver-storage-scsi
Summary: Storage driver plugin for local scsi devices
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description daemon-driver-storage-scsi
The storage driver backend adding implementation of the storage APIs for scsi
host devices.

%package daemon-driver-storage-iscsi
Summary: Storage driver plugin for iscsi
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: iscsi-initiator-utils

%description daemon-driver-storage-iscsi
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using the host iscsi stack.

%if %{with_storage_iscsi_direct}
%package daemon-driver-storage-iscsi-direct
Summary: Storage driver plugin for iscsi-direct
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description daemon-driver-storage-iscsi-direct
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using libiscsi direct connection.
%endif

%package daemon-driver-storage-mpath
Summary: Storage driver plugin for multipath volumes
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: device-mapper

%description daemon-driver-storage-mpath
The storage driver backend adding implementation of the storage APIs for
multipath storage using device mapper.

%if %{with_storage_gluster}
%package daemon-driver-storage-gluster
Summary: Storage driver plugin for gluster
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
    %if 0%{?fedora}
Requires: glusterfs-client >= 2.0.1
    %endif
    %if (0%{?fedora} || 0%{?with_storage_gluster})
Requires: /usr/sbin/gluster
    %endif

%description daemon-driver-storage-gluster
The storage driver backend adding implementation of the storage APIs for gluster
volumes using libgfapi.
%endif

%if %{with_storage_rbd}
%package daemon-driver-storage-rbd
Summary: Storage driver plugin for rbd
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description daemon-driver-storage-rbd
The storage driver backend adding implementation of the storage APIs for rbd
volumes using the ceph protocol.
%endif

%if %{with_storage_zfs}
%package daemon-driver-storage-zfs
Summary: Storage driver plugin for ZFS
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
# Support any conforming implementation of zfs
Requires: /sbin/zfs
Requires: /sbin/zpool

%description daemon-driver-storage-zfs
The storage driver backend adding implementation of the storage APIs for
ZFS volumes.
%endif

%package daemon-driver-storage
Summary: Storage driver plugin including all backends for the libvirtd daemon
Requires: libvirt-daemon-driver-storage-core = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage-disk = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage-logical = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage-scsi = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage-iscsi = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage-mpath = %{epoch}:%{version}-%{release}
%if %{with_storage_iscsi_direct}
Requires: libvirt-daemon-driver-storage-iscsi-direct = %{epoch}:%{version}-%{release}
%endif
%if %{with_storage_gluster}
Requires: libvirt-daemon-driver-storage-gluster = %{epoch}:%{version}-%{release}
%endif
%if %{with_storage_rbd}
Requires: libvirt-daemon-driver-storage-rbd = %{epoch}:%{version}-%{release}
%endif
%if %{with_storage_zfs}
Requires: libvirt-daemon-driver-storage-zfs = %{epoch}:%{version}-%{release}
%endif

%description daemon-driver-storage
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using LVM, iSCSI,
parted and more.

%if %{with_qemu}
%package daemon-driver-qemu
Summary: QEMU driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: /usr/bin/qemu-img
# For image compression
Requires: gzip
Requires: bzip2
Requires: lzop
Requires: xz
Requires: systemd-container
Requires: swtpm-tools
    %if (0%{?fedora} >= 36) || (0%{?rhel} >= 9)
Recommends: passt
Recommends: passt-selinux
    %endif

%description daemon-driver-qemu
The qemu driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
QEMU
%endif

%if %{with_lxc}
%package daemon-driver-lxc
Summary: LXC driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: systemd-container

%description daemon-driver-lxc
The LXC driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
the Linux kernel
%endif

%if %{with_vbox}
%package daemon-driver-vbox
Summary: VirtualBox driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description daemon-driver-vbox
The vbox driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
VirtualBox
%endif

%if %{with_libxl}
%package daemon-driver-libxl
Summary: Libxl driver plugin for the libvirtd daemon
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Obsoletes: libvirt-daemon-driver-xen < 4.3.0

%description daemon-driver-libxl
The Libxl driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Libxl
%endif

%if %{with_qemu_tcg}
%package daemon-qemu
Summary: Server side daemon & driver required to run QEMU guests

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-qemu = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{epoch}:%{version}-%{release}
Requires: qemu

%description daemon-qemu
Server side daemon and driver required to manage the virtualization
capabilities of the QEMU TCG emulators
%endif

%if %{with_qemu_kvm}
%package daemon-kvm
Summary: Server side daemon & driver required to run KVM guests

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-qemu = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{epoch}:%{version}-%{release}
Requires: qemu-kvm

%description daemon-kvm
Server side daemon and driver required to manage the virtualization
capabilities of the KVM hypervisor
%endif

%if %{with_lxc}
%package daemon-lxc
Summary: Server side daemon & driver required to run LXC guests

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-lxc = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{epoch}:%{version}-%{release}

%description daemon-lxc
Server side daemon and driver required to manage the virtualization
capabilities of LXC
%endif

%if %{with_libxl}
%package daemon-xen
Summary: Server side daemon & driver required to run XEN guests

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-libxl = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{epoch}:%{version}-%{release}
Requires: xen

%description daemon-xen
Server side daemon and driver required to manage the virtualization
capabilities of XEN
%endif

%if %{with_vbox}
%package daemon-vbox
Summary: Server side daemon & driver required to run VirtualBox guests

Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-vbox = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{epoch}:%{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{epoch}:%{version}-%{release}

%description daemon-vbox
Server side daemon and driver required to manage the virtualization
capabilities of VirtualBox
%endif

%package client
Summary: Client side utilities of the libvirt library
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
# Needed by virt-pki-validate script.
Requires: gnutls-utils

# Ensure smooth upgrades
Obsoletes: libvirt-bash-completion < 7.3.0

%description client
The client binaries needed to access the virtualization
capabilities of recent versions of Linux (and other OSes).

%package client-qemu
Summary: Additional client side utilities for QEMU
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: python3-libvirt >= 3.7.0
Requires: python3-cryptography
Requires: python3-lxml

%description client-qemu
The additional client binaries are used to interact
with some QEMU specific features of libvirt.

%package libs
Summary: Client side libraries
# So remote clients can access libvirt over SSH tunnel
Requires: cyrus-sasl
# Needed by default sasl.conf - no onerous extra deps, since
# 100's of other things on a system already pull in krb5-libs
Requires: cyrus-sasl-gssapi

%description libs
Shared libraries for accessing the libvirt daemon.

%if %{with_wireshark}
%package wireshark
Summary: Wireshark dissector plugin for libvirt RPC transactions
Requires: wireshark
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description wireshark
Wireshark dissector plugin for better analysis of libvirt RPC traffic.
%endif

%if %{with_lxc}
%package login-shell
Summary: Login shell for connecting users to an LXC container
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description login-shell
Provides the set-uid virt-login-shell binary that is used to
connect a user to an LXC container when they login, by switching
namespaces.
%endif

%package devel
Summary: Libraries, includes, etc. to compile with the libvirt library
Requires: libvirt-libs = %{epoch}:%{version}-%{release}
Requires: pkgconfig

%description devel
Include header files & development libraries for the libvirt C library.

%if %{with_sanlock}
%package lock-sanlock
Summary: Sanlock lock manager plugin for QEMU driver
Requires: sanlock >= 2.4
#for virt-sanlock-cleanup require augeas
Requires: augeas
Requires: libvirt-daemon = %{epoch}:%{version}-%{release}
Requires: libvirt-libs = %{epoch}:%{version}-%{release}

%description lock-sanlock
Includes the Sanlock lock manager plugin for the QEMU
driver
%endif

%package nss
Summary: Libvirt plugin for Name Service Switch
Requires: libvirt-daemon-driver-network = %{epoch}:%{version}-%{release}

%description nss
Libvirt plugin for NSS for translating domain names into IP addresses.

%if %{with_mingw}
%package -n mingw32-libvirt
Summary: %{summary}
Obsoletes: mingw32-libvirt-static < 7.0.0
BuildArch: noarch

%description -n mingw32-libvirt
MinGW Windows libvirt virtualization library.

%package -n mingw64-libvirt
Summary: %{summary}
Obsoletes: mingw64-libvirt-static < 7.0.0
BuildArch: noarch

%description -n mingw64-libvirt
MinGW Windows libvirt virtualization library.

%{?mingw_debug_package}
%endif

%prep

%autosetup -S git_am -N

ExtractPatches()
{
    local patchtarball=$1

    if [ ! -f $patchtarball ]; then
        echo "ExtractPatches"
        exit 1
    fi
    tar xf $patchtarball
}
ExtractPatches %{SOURCE1}

for p in patches/*.patch; do
    patch -p1 -F1 -s < $p
done

# "make dist" replaces all symlinks with a copy of the linked files;
# we need to replace all of them with the original symlinks
echo "Restoring symlinks"
while read lnk target; do
    if [ -e $lnk ]; then
        rm -rf $lnk
        ln -s $target $lnk
    fi
done <%{_sourcedir}/symlinks || exit 1
git add .
git commit -q -a --allow-empty --author 'rpm-build <rpm-build>' -m symlinks

git config gc.auto 0

%autopatch

%build
%if 0%{?fedora} >= %{min_fedora} || 0%{?rhel} >= %{min_rhel}
    %define supported_platform 1
%else
    %define supported_platform 0
%endif

%if ! %{supported_platform}
echo "This RPM requires either Fedora >= %{min_fedora} or RHEL >= %{min_rhel}"
exit 1
%endif

%if %{with_qemu}
    %define arg_qemu -Ddriver_qemu=enabled
%else
    %define arg_qemu -Ddriver_qemu=disabled
%endif

%if %{with_openvz}
    %define arg_openvz -Ddriver_openvz=enabled
%else
    %define arg_openvz -Ddriver_openvz=disabled
%endif

%if %{with_lxc}
    %define arg_lxc -Ddriver_lxc=enabled
    %define arg_login_shell -Dlogin_shell=enabled
%else
    %define arg_lxc -Ddriver_lxc=disabled
    %define arg_login_shell -Dlogin_shell=disabled
%endif

%if %{with_vbox}
    %define arg_vbox -Ddriver_vbox=enabled
%else
    %define arg_vbox -Ddriver_vbox=disabled
%endif

%if %{with_libxl}
    %define arg_libxl -Ddriver_libxl=enabled
%else
    %define arg_libxl -Ddriver_libxl=disabled
%endif

%if %{with_esx}
    %define arg_esx -Ddriver_esx=enabled -Dcurl=enabled
%else
    %define arg_esx -Ddriver_esx=disabled -Dcurl=disabled
%endif

%if %{with_hyperv}
    %define arg_hyperv -Ddriver_hyperv=enabled -Dopenwsman=enabled
%else
    %define arg_hyperv -Ddriver_hyperv=disabled -Dopenwsman=disabled
%endif

%if %{with_vmware}
    %define arg_vmware -Ddriver_vmware=enabled
%else
    %define arg_vmware -Ddriver_vmware=disabled
%endif

%if %{with_storage_rbd}
    %define arg_storage_rbd -Dstorage_rbd=enabled
%else
    %define arg_storage_rbd -Dstorage_rbd=disabled
%endif

%if %{with_storage_gluster}
    %define arg_storage_gluster -Dstorage_gluster=enabled -Dglusterfs=enabled
%else
    %define arg_storage_gluster -Dstorage_gluster=disabled -Dglusterfs=disabled
%endif

%if %{with_storage_zfs}
    %define arg_storage_zfs -Dstorage_zfs=enabled
%else
    %define arg_storage_zfs -Dstorage_zfs=disabled
%endif

%if %{with_numactl}
    %define arg_numactl -Dnumactl=enabled
%else
    %define arg_numactl -Dnumactl=disabled
%endif

%if %{with_numad}
    %define arg_numad -Dnumad=enabled
%else
    %define arg_numad -Dnumad=disabled
%endif

%if %{with_fuse}
    %define arg_fuse -Dfuse=enabled
%else
    %define arg_fuse -Dfuse=disabled
%endif

%if %{with_sanlock}
    %define arg_sanlock -Dsanlock=enabled
%else
    %define arg_sanlock -Dsanlock=disabled
%endif

%if %{with_firewalld_zone}
    %define arg_firewalld_zone -Dfirewalld_zone=enabled
%else
    %define arg_firewalld_zone -Dfirewalld_zone=disabled
%endif

%if %{with_netcf}
    %define arg_netcf -Dnetcf=enabled
%else
    %define arg_netcf -Dnetcf=disabled
%endif

%if %{with_wireshark}
    %define arg_wireshark -Dwireshark_dissector=enabled
%else
    %define arg_wireshark -Dwireshark_dissector=disabled
%endif

%if %{with_storage_iscsi_direct}
    %define arg_storage_iscsi_direct -Dstorage_iscsi_direct=enabled -Dlibiscsi=enabled
%else
    %define arg_storage_iscsi_direct -Dstorage_iscsi_direct=disabled -Dlibiscsi=disabled
%endif

%if %{with_libssh}
    %define arg_libssh -Dlibssh=enabled
%else
    %define arg_libssh -Dlibssh=disabled
%endif

%if %{with_libssh2}
    %define arg_libssh2 -Dlibssh2=enabled
%else
    %define arg_libssh2 -Dlibssh2=disabled
%endif

%if %{with_modular_daemons}
    %define arg_remote_mode -Dremote_default_mode=direct
%else
    %define arg_remote_mode -Dremote_default_mode=legacy
%endif

%define when  %(date +"%%F-%%T")
%define where %(hostname)
%define who   %{?packager}%{!?packager:Unknown}
%define arg_packager -Dpackager="%{who}, %{when}, %{where}"
%define arg_packager_version -Dpackager_version="%{release}"
%define arg_selinux_mount -Dselinux_mount="/sys/fs/selinux"

# place macros above and build commands below this comment

export SOURCE_DATE_EPOCH=$(stat --printf='%Y' %{_specdir}/tdx-libvirt.spec)

%meson \
           -Drunstatedir=%{_rundir} \
           %{?arg_qemu} \
           %{?arg_openvz} \
           %{?arg_lxc} \
           %{?arg_vbox} \
           %{?arg_libxl} \
           -Dsasl=enabled \
           -Dpolkit=enabled \
           -Ddriver_libvirtd=enabled \
           -Ddriver_remote=enabled \
           -Ddriver_test=enabled \
           %{?arg_esx} \
           %{?arg_hyperv} \
           %{?arg_vmware} \
           -Ddriver_vz=disabled \
           -Ddriver_bhyve=disabled \
           -Ddriver_ch=disabled \
           %{?arg_remote_mode} \
           -Ddriver_interface=enabled \
           -Ddriver_network=enabled \
           -Dstorage_fs=enabled \
           -Dstorage_lvm=enabled \
           -Dstorage_iscsi=enabled \
           %{?arg_storage_iscsi_direct} \
           -Dstorage_scsi=enabled \
           -Dstorage_disk=enabled \
           -Dstorage_mpath=enabled \
           %{?arg_storage_rbd} \
           %{?arg_storage_gluster} \
           %{?arg_storage_zfs} \
           -Dstorage_vstorage=disabled \
           -Dstorage_sheepdog=disabled \
           %{?arg_numactl} \
           %{?arg_numad} \
           -Dcapng=enabled \
           %{?arg_fuse} \
           %{?arg_netcf} \
           -Dselinux=enabled \
           %{?arg_selinux_mount} \
           -Dapparmor=disabled \
           -Dapparmor_profiles=disabled \
           -Dsecdriver_apparmor=disabled \
           -Dsecdriver_selinux=disabled \
           -Dselinux=disabled \
           -Dudev=enabled \
           -Dyajl=enabled \
           %{?arg_sanlock} \
           -Dlibpcap=enabled \
           -Dlibnl=enabled \
           -Daudit=enabled \
           -Ddtrace=enabled \
           -Dfirewalld=enabled \
           %{?arg_firewalld_zone} \
           %{?arg_wireshark} \
           %{?arg_libssh} \
           %{?arg_libssh2} \
           -Dpm_utils=disabled \
           -Dnss=enabled \
           %{arg_packager} \
           %{arg_packager_version} \
           -Dqemu_user=%{qemu_user} \
           -Dqemu_group=%{qemu_group} \
           -Dqemu_moddir=%{qemu_moddir} \
           -Dqemu_datadir=%{qemu_datadir} \
           -Dtls_priority=%{tls_priority} \
           %{?enable_werror} \
           -Dexpensive_tests=enabled \
           -Dinit_script=systemd \
           -Ddocs=enabled \
           -Dtests=enabled \
           -Drpath=disabled \
           %{?arg_login_shell}

%meson_build

%if %{with_mingw}
%mingw_meson \
  --auto-features=enabled \
  -Ddriver_remote=enabled \
  -Ddriver_test=enabled \
  -Ddriver_esx=enabled \
  -Dcurl=enabled \
  -Ddocs=enabled \
  -Dapparmor=disabled \
  -Dapparmor_profiles=disabled \
  -Dattr=disabled \
  -Daudit=disabled \
  -Dbash_completion=disabled \
  -Dblkid=disabled \
  -Dcapng=disabled \
  -Ddriver_bhyve=disabled \
  -Ddriver_hyperv=disabled \
  -Ddriver_interface=disabled \
  -Ddriver_libvirtd=disabled \
  -Ddriver_libxl=disabled \
  -Ddriver_lxc=disabled \
  -Ddriver_network=disabled \
  -Ddriver_openvz=disabled \
  -Ddriver_qemu=disabled \
  -Ddriver_secrets=disabled \
  -Ddriver_vbox=disabled \
  -Ddriver_vmware=disabled \
  -Ddriver_vz=disabled \
  -Ddtrace=disabled \
  -Dexpensive_tests=enabled \
  -Dfirewalld=disabled \
  -Dfirewalld_zone=disabled \
  -Dfuse=disabled \
  -Dglusterfs=disabled \
  -Dhost_validate=disabled \
  -Dlibiscsi=disabled \
  -Dlibnl=disabled \
  -Dlibpcap=disabled \
  -Dlibssh2=disabled \
  -Dlibssh=disabled \
  -Dlogin_shell=disabled \
  -Dnetcf=disabled \
  -Dnls=disabled \
  -Dnss=disabled \
  -Dnumactl=disabled \
  -Dnumad=disabled \
  -Dopenwsman=disabled \
  -Dpciaccess=disabled \
  -Dpm_utils=disabled \
  -Dpolkit=disabled \
  -Dreadline=disabled \
  -Drpath=disabled \
  -Dsanlock=disabled \
  -Dsasl=disabled \
  -Dsecdriver_apparmor=disabled \
  -Dsecdriver_selinux=disabled \
  -Dselinux=disabled \
  -Dstorage_dir=disabled \
  -Dstorage_disk=disabled \
  -Dstorage_fs=disabled \
  -Dstorage_gluster=disabled \
  -Dstorage_iscsi_direct=disabled \
  -Dstorage_iscsi=disabled \
  -Dstorage_lvm=disabled \
  -Dstorage_mpath=disabled \
  -Dstorage_rbd=disabled \
  -Dstorage_scsi=disabled \
  -Dstorage_vstorage=disabled \
  -Dstorage_zfs=disabled \
  -Dsysctl_config=disabled \
  -Dtests=disabled \
  -Dudev=disabled \
  -Dwireshark_dissector=disabled \
  -Dyajl=disabled
%mingw_ninja
%endif

%install
rm -fr %{buildroot}

export SOURCE_DATE_EPOCH=$(stat --printf='%Y' %{_specdir}/tdx-libvirt.spec)

%meson_install

# We don't want to install /etc/libvirt/qemu/networks in the main %%files list
# because if the admin wants to delete the default network completely, we don't
# want to end up re-incarnating it on every RPM upgrade.
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/
cp $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml \
   $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
# libvirt saves this file with mode 0600
chmod 0600 $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml

# nwfilter files are installed in /usr/share/libvirt and copied to /etc in %%post
# to avoid verification errors on changed files in /etc
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
cp -a $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml \
    $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
# libvirt saves these files with mode 600
chmod 600 $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml

%if ! %{with_qemu}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_qemu.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%endif
%find_lang %{name}

%if ! %{with_sanlock}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirt_sanlock.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%endif

%if ! %{with_lxc}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_lxc.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%endif

%if ! %{with_qemu}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.qemu
%endif
%if ! %{with_lxc}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/lxc.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.lxc
%endif
%if ! %{with_libxl}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/libxl.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.libxl
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_libxl.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%endif

# Copied into libvirt-docs subpackage eventually
mv $RPM_BUILD_ROOT%{_datadir}/doc/libvirt libvirt-docs

%ifarch %{arches_systemtap_64bit}
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes-64.stp

    %if %{with_qemu}
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes-64.stp
    %endif
%endif

%if %{with_mingw}
%mingw_ninja_install

rm -rf $RPM_BUILD_ROOT%{mingw32_sysconfdir}/libvirt/nwfilter
rm -rf $RPM_BUILD_ROOT%{mingw64_sysconfdir}/libvirt/nwfilter
rm -rf $RPM_BUILD_ROOT%{mingw32_datadir}/doc/*
rm -rf $RPM_BUILD_ROOT%{mingw64_datadir}/doc/*
rm -rf $RPM_BUILD_ROOT%{mingw32_datadir}/gtk-doc/*
rm -rf $RPM_BUILD_ROOT%{mingw64_datadir}/gtk-doc/*

rm -rf $RPM_BUILD_ROOT%{mingw32_libexecdir}/libvirt_iohelper.exe
rm -rf $RPM_BUILD_ROOT%{mingw64_libexecdir}/libvirt_iohelper.exe
rm -rf $RPM_BUILD_ROOT%{mingw32_libexecdir}/libvirt-guests.sh
rm -rf $RPM_BUILD_ROOT%{mingw64_libexecdir}/libvirt-guests.sh

%mingw_debug_install_post

%mingw_find_lang %{name}

%endif

%define libvirt_daemon_schedule_restart() mkdir -p %{_localstatedir}/lib/rpm-state/libvirt || : \
/bin/systemctl is-active %1.service 1>/dev/null 2>&1 && \
  touch %{_localstatedir}/lib/rpm-state/libvirt/restart-%1 || :

%define libvirt_daemon_finish_restart() rm -f %{_localstatedir}/lib/rpm-state/libvirt/restart-%1 \
rmdir %{_localstatedir}/lib/rpm-state/libvirt 2>/dev/null || :

%define libvirt_daemon_needs_restart() -f %{_localstatedir}/lib/rpm-state/libvirt/restart-%1

%define libvirt_daemon_perform_restart() if test %libvirt_daemon_needs_restart %1 \
then \
  /bin/systemctl try-restart %1.service >/dev/null 2>&1 || : \
fi \
%libvirt_daemon_finish_restart %1

# For daemons with only UNIX sockets
%define libvirt_daemon_systemd_post() %systemd_post %1.socket %1-ro.socket %1-admin.socket %1.service
%define libvirt_daemon_systemd_preun() %systemd_preun %1.service %1-ro.socket %1-admin.socket %1.socket

# For daemons with UNIX and INET sockets
%define libvirt_daemon_systemd_post_inet() %systemd_post %1.socket %1-ro.socket %1-admin.socket %1-tls.socket %1-tcp.socket %1.service
%define libvirt_daemon_systemd_preun_inet() %systemd_preun %1.service %1-ro.socket %1-admin.socket %1-tls.socket %1-tcp.socket %1.socket

# For daemons with only UNIX sockets and no unprivileged read-only access
%define libvirt_daemon_systemd_post_priv() %systemd_post %1.socket %1-admin.socket %1.service
%define libvirt_daemon_systemd_preun_priv() %systemd_preun %1.service %1-admin.socket %1.socket

%pre daemon
%libvirt_sysconfig_pre libvirtd virtproxyd virtlogd virtlockd libvirt-guests
# 'libvirt' group is just to allow password-less polkit access to
# libvirtd. The uid number is irrelevant, so we use dynamic allocation
# described at the above link.
getent group libvirt >/dev/null || groupadd -r libvirt
exit 0

%post daemon
%libvirt_daemon_systemd_post_priv virtlogd
%libvirt_daemon_systemd_post_priv virtlockd
%if %{with_modular_daemons}
%libvirt_daemon_systemd_post_inet virtproxyd
%else
%libvirt_daemon_systemd_post_inet libvirtd
%endif
%systemd_post libvirt-guests.service
%libvirt_daemon_schedule_restart libvirtd

%preun daemon
%systemd_preun libvirt-guests.service
%libvirt_daemon_systemd_preun_inet libvirtd
%libvirt_daemon_systemd_preun_inet virtproxyd
%libvirt_daemon_systemd_preun_priv virtlogd
%libvirt_daemon_systemd_preun_priv virtlockd

%postun daemon
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    /bin/systemctl reload-or-try-restart virtlockd.service virtlogd.service >/dev/null 2>&1 || :
fi
%systemd_postun libvirt-guests.service

%posttrans daemon
%libvirt_sysconfig_posttrans libvirtd virtproxyd virtlogd virtlockd libvirt-guests
if test %libvirt_daemon_needs_restart libvirtd
then
    # See if user has previously modified their install to
    # tell libvirtd to use --listen
    grep -E '^LIBVIRTD_ARGS=.*--listen' /etc/sysconfig/libvirtd 1>/dev/null 2>&1
    if test $? = 0
    then
        # Then lets keep honouring --listen and *not* use
        # systemd socket activation, because switching things
        # might confuse mgmt tool like puppet/ansible that
        # expect the old style libvirtd
        /bin/systemctl mask \
                libvirtd.socket \
                libvirtd-ro.socket \
                libvirtd-admin.socket \
                libvirtd-tls.socket \
                libvirtd-tcp.socket >/dev/null 2>&1 || :
        /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
    else
        # Old libvirtd owns the sockets and will delete them on
        # shutdown. Can't use a try-restart as libvirtd will simply
        # own the sockets again when it comes back up. Thus we must
        # do this particular ordering, so that we get libvirtd
        # running with socket activation in use
        /bin/systemctl stop libvirtd.service >/dev/null 2>&1 || :
        /bin/systemctl try-restart \
                libvirtd.socket \
                libvirtd-ro.socket \
                libvirtd-admin.socket >/dev/null 2>&1 || :
        /bin/systemctl start libvirtd.service >/dev/null 2>&1 || :
    fi
fi
%libvirt_daemon_finish_restart libvirtd

%pre daemon-driver-network
%libvirt_sysconfig_pre virtnetworkd

%post daemon-driver-network
%if %{with_firewalld_zone}
    %firewalld_reload
%endif

%if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtnetworkd
%endif
%libvirt_daemon_schedule_restart virtnetworkd

%preun daemon-driver-network
%libvirt_daemon_systemd_preun virtnetworkd

%postun daemon-driver-network
%if %{with_firewalld_zone}
    %firewalld_reload
%endif

%posttrans daemon-driver-network
%libvirt_sysconfig_posttrans virtnetworkd
%libvirt_daemon_perform_restart virtnetworkd

%pre daemon-driver-nwfilter
%libvirt_sysconfig_pre virtnwfilterd

%post daemon-driver-nwfilter
%if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtnwfilterd
%endif
%libvirt_daemon_schedule_restart virtnwfilterd

%preun daemon-driver-nwfilter
%libvirt_daemon_systemd_preun virtnwfilterd

%posttrans daemon-driver-nwfilter
%libvirt_sysconfig_posttrans virtnwfilterd
%libvirt_daemon_perform_restart virtnwfilterd

%pre daemon-driver-nodedev
%libvirt_sysconfig_pre virtnodedevd

%post daemon-driver-nodedev
%if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtnodedevd
%endif
%libvirt_daemon_schedule_restart virtnodedevd

%preun daemon-driver-nodedev
%libvirt_daemon_systemd_preun virtnodedevd

%posttrans daemon-driver-nodedev
%libvirt_sysconfig_posttrans virtnodedevd
%libvirt_daemon_perform_restart virtnodedevd

%pre daemon-driver-interface
%libvirt_sysconfig_pre virtinterfaced

%post daemon-driver-interface
%if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtinterfaced
%endif
%libvirt_daemon_schedule_restart virtinterfaced

%preun daemon-driver-interface
%libvirt_daemon_systemd_preun virtinterfaced

%posttrans daemon-driver-interface
%libvirt_sysconfig_posttrans virtinterfaced
%libvirt_daemon_perform_restart virtinterfaced

%pre daemon-driver-secret
%libvirt_sysconfig_pre virtsecretd

%post daemon-driver-secret
%if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtsecretd
%endif
%libvirt_daemon_schedule_restart virtsecretd

%preun daemon-driver-secret
%libvirt_daemon_systemd_preun virtsecretd

%posttrans daemon-driver-secret
%libvirt_sysconfig_posttrans virtsecretd
%libvirt_daemon_perform_restart virtsecretd

%pre daemon-driver-storage-core
%libvirt_sysconfig_pre virtstoraged

%post daemon-driver-storage-core
%if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtstoraged
%endif
%libvirt_daemon_schedule_restart virtstoraged

%preun daemon-driver-storage-core
%libvirt_daemon_systemd_preun virtstoraged

%posttrans daemon-driver-storage-core
%libvirt_sysconfig_posttrans virtstoraged
%libvirt_daemon_perform_restart virtstoraged

%if %{with_qemu}
%pre daemon-driver-qemu
%libvirt_sysconfig_pre virtqemud
# We want soft static allocation of well-known ids, as disk images
# are commonly shared across NFS mounts by id rather than name; see
# https://fedoraproject.org/wiki/Packaging:UsersAndGroups
getent group kvm >/dev/null || groupadd -f -g 36 -r kvm
getent group qemu >/dev/null || groupadd -f -g 107 -r qemu
if ! getent passwd qemu >/dev/null; then
  if ! getent passwd 107 >/dev/null; then
    useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  else
    useradd -r -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  fi
fi
exit 0

%post daemon-driver-qemu
    %if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtqemud
    %endif
%libvirt_daemon_schedule_restart virtqemud

%preun daemon-driver-qemu
%libvirt_daemon_systemd_preun virtqemud

%posttrans daemon-driver-qemu
%libvirt_sysconfig_posttrans virtqemud
%libvirt_daemon_perform_restart virtqemud
%endif

%if %{with_lxc}
%pre daemon-driver-lxc
%libvirt_sysconfig_pre virtlxcd

%post daemon-driver-lxc
    %if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtlxcd
    %endif
%libvirt_daemon_schedule_restart virtlxcd

%preun daemon-driver-lxc
%libvirt_daemon_systemd_preun virtlxcd

%posttrans daemon-driver-lxc
%libvirt_sysconfig_posttrans virtlxcd
%libvirt_daemon_perform_restart virtlxcd
%endif

%if %{with_vbox}
%post daemon-driver-vbox
    %if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtvboxd
    %endif
%libvirt_daemon_schedule_restart virtvboxd

%pre daemon-driver-vbox
%libvirt_sysconfig_pre virtvboxd

%preun daemon-driver-vbox
%libvirt_daemon_systemd_preun virtvboxd

%posttrans daemon-driver-vbox
%libvirt_sysconfig_posttrans virtvboxd
%libvirt_daemon_perform_restart virtvboxd
%endif

%if %{with_libxl}
%post daemon-driver-libxl
    %if %{with_modular_daemons}
%libvirt_daemon_systemd_post virtxend
    %endif
%libvirt_daemon_schedule_restart virtxend

%pre daemon-driver-libxl
%libvirt_sysconfig_pre virtxend

%preun daemon-driver-libxl
%libvirt_daemon_systemd_preun virtxend

%posttrans daemon-driver-libxl
%libvirt_sysconfig_posttrans virtxend
%libvirt_daemon_perform_restart virtxend
%endif

%post daemon-config-network
if test $1 -eq 1 && test ! -f %{_sysconfdir}/libvirt/qemu/networks/default.xml ; then
    # see if the network used by default network creates a conflict,
    # and try to resolve it
    # NB: 192.168.122.0/24 is used in the default.xml template file;
    # do not modify any of those values here without also modifying
    # them in the template.
    orig_sub=122
    sub=${orig_sub}
    nl='
'
    routes="${nl}$(ip route show | cut -d' ' -f1)${nl}"
    case ${routes} in
      *"${nl}192.168.${orig_sub}.0/24${nl}"*)
        # there was a match, so we need to look for an unused subnet
        for new_sub in $(seq 124 254); do
          case ${routes} in
          *"${nl}192.168.${new_sub}.0/24${nl}"*)
            ;;
          *)
            sub=$new_sub
            break;
            ;;
          esac
        done
        ;;
      *)
        ;;
    esac

    sed -e "s/${orig_sub}/${sub}/g" \
         < %{_datadir}/libvirt/networks/default.xml \
         > %{_sysconfdir}/libvirt/qemu/networks/default.xml
    ln -s ../default.xml %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml
    # libvirt saves this file with mode 0600
    chmod 0600 %{_sysconfdir}/libvirt/qemu/networks/default.xml

    # Make sure libvirt picks up the new network defininiton
    %libvirt_daemon_schedule_restart libvirtd
    %libvirt_daemon_schedule_restart virtnetworkd
fi

%posttrans daemon-config-network
%libvirt_daemon_perform_restart libvirtd
%libvirt_daemon_perform_restart virtnetworkd

%post daemon-config-nwfilter
for datadir_file in %{_datadir}/libvirt/nwfilter/*.xml; do
  sysconfdir_file=%{_sysconfdir}/libvirt/nwfilter/$(basename "$datadir_file")
  if [ ! -f "$sysconfdir_file" ]; then
    # libvirt saves these files with mode 600
    install -m 0600 "$datadir_file" "$sysconfdir_file"
  fi
done
# Make sure libvirt picks up the new nwfilter defininitons
%libvirt_daemon_schedule_restart libvirtd
%libvirt_daemon_schedule_restart virtnwfilterd

%posttrans daemon-config-nwfilter
%libvirt_daemon_perform_restart libvirtd
%libvirt_daemon_perform_restart virtnwfilterd

%if %{with_lxc}
%pre login-shell
getent group virtlogin >/dev/null || groupadd -r virtlogin
exit 0
%endif

%files

%files docs
%doc AUTHORS.rst NEWS.rst README.rst
%doc libvirt-docs/*

%files daemon
%{_unitdir}/libvirtd.service
%{_unitdir}/libvirtd.socket
%{_unitdir}/libvirtd-ro.socket
%{_unitdir}/libvirtd-admin.socket
%{_unitdir}/libvirtd-tcp.socket
%{_unitdir}/libvirtd-tls.socket
%{_unitdir}/virtproxyd.service
%{_unitdir}/virtproxyd.socket
%{_unitdir}/virtproxyd-ro.socket
%{_unitdir}/virtproxyd-admin.socket
%{_unitdir}/virtproxyd-tcp.socket
%{_unitdir}/virtproxyd-tls.socket
%{_unitdir}/virt-guest-shutdown.target
%{_unitdir}/virtlogd.service
%{_unitdir}/virtlogd.socket
%{_unitdir}/virtlogd-admin.socket
%{_unitdir}/virtlockd.service
%{_unitdir}/virtlockd.socket
%{_unitdir}/virtlockd-admin.socket
%{_unitdir}/libvirt-guests.service
%config(noreplace) %{_sysconfdir}/libvirt/libvirtd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtproxyd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlogd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlockd.conf
%config(noreplace) %{_sysconfdir}/sasl2/libvirt.conf
%config(noreplace) %{_prefix}/lib/sysctl.d/60-libvirtd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd
%dir %{_datadir}/libvirt/
%ghost %dir %{_rundir}/libvirt/
%ghost %dir %{_rundir}/libvirt/common/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/images/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/filesystems/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/boot/
%dir %attr(0711, root, root) %{_localstatedir}/cache/libvirt/
%dir %attr(0755, root, root) %{_libdir}/libvirt/
%dir %attr(0755, root, root) %{_libdir}/libvirt/connection-driver/
%dir %attr(0755, root, root) %{_libdir}/libvirt/lock-driver/
%dir %attr(0755, root, root) %{_libdir}/libvirt/storage-backend/
%dir %attr(0755, root, root) %{_libdir}/libvirt/storage-file/
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/lockd.so
%{_datadir}/augeas/lenses/libvirtd.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd.aug
%{_datadir}/augeas/lenses/virtlogd.aug
%{_datadir}/augeas/lenses/tests/test_virtlogd.aug
%{_datadir}/augeas/lenses/virtlockd.aug
%{_datadir}/augeas/lenses/tests/test_virtlockd.aug
%{_datadir}/augeas/lenses/virtproxyd.aug
%{_datadir}/augeas/lenses/tests/test_virtproxyd.aug
%{_datadir}/augeas/lenses/libvirt_lockd.aug
%if %{with_qemu}
%{_datadir}/augeas/lenses/tests/test_libvirt_lockd.aug
%endif
%{_datadir}/polkit-1/actions/org.libvirt.unix.policy
%{_datadir}/polkit-1/actions/org.libvirt.api.policy
%{_datadir}/polkit-1/rules.d/50-libvirt.rules
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/
%attr(0755, root, root) %{_libexecdir}/libvirt_iohelper
%attr(0755, root, root) %{_bindir}/virt-ssh-helper
%attr(0755, root, root) %{_sbindir}/libvirtd
%attr(0755, root, root) %{_sbindir}/virtproxyd
%attr(0755, root, root) %{_sbindir}/virtlogd
%attr(0755, root, root) %{_sbindir}/virtlockd
%attr(0755, root, root) %{_libexecdir}/libvirt-guests.sh
%{_mandir}/man1/virt-admin.1*
%{_mandir}/man1/virt-host-validate.1*
%{_mandir}/man8/virt-ssh-helper.8*
%{_mandir}/man8/libvirt-guests.8*
%{_mandir}/man8/libvirtd.8*
%{_mandir}/man8/virtlogd.8*
%{_mandir}/man8/virtlockd.8*
%{_mandir}/man8/virtproxyd.8*
%{_bindir}/virt-host-validate
%{_bindir}/virt-admin
%{_datadir}/bash-completion/completions/virt-admin

%files daemon-config-network
%dir %{_datadir}/libvirt/networks/
%{_datadir}/libvirt/networks/default.xml
%ghost %{_sysconfdir}/libvirt/qemu/networks/default.xml
%ghost %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml

%files daemon-config-nwfilter
%dir %{_datadir}/libvirt/nwfilter/
%{_datadir}/libvirt/nwfilter/*.xml
%ghost %{_sysconfdir}/libvirt/nwfilter/*.xml

%files daemon-driver-interface
%config(noreplace) %{_sysconfdir}/libvirt/virtinterfaced.conf
%{_datadir}/augeas/lenses/virtinterfaced.aug
%{_datadir}/augeas/lenses/tests/test_virtinterfaced.aug
%{_unitdir}/virtinterfaced.service
%{_unitdir}/virtinterfaced.socket
%{_unitdir}/virtinterfaced-ro.socket
%{_unitdir}/virtinterfaced-admin.socket
%attr(0755, root, root) %{_sbindir}/virtinterfaced
%ghost %dir %{_rundir}/libvirt/interface/
%{_libdir}/libvirt/connection-driver/libvirt_driver_interface.so
%{_mandir}/man8/virtinterfaced.8*

%files daemon-driver-network
%config(noreplace) %{_sysconfdir}/libvirt/virtnetworkd.conf
%{_datadir}/augeas/lenses/virtnetworkd.aug
%{_datadir}/augeas/lenses/tests/test_virtnetworkd.aug
%{_unitdir}/virtnetworkd.service
%{_unitdir}/virtnetworkd.socket
%{_unitdir}/virtnetworkd-ro.socket
%{_unitdir}/virtnetworkd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtnetworkd
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/autostart
%ghost %dir %{_rundir}/libvirt/network/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/network/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/dnsmasq/
%attr(0755, root, root) %{_libexecdir}/libvirt_leaseshelper
%{_libdir}/libvirt/connection-driver/libvirt_driver_network.so
%{_mandir}/man8/virtnetworkd.8*
%if %{with_firewalld_zone}
%{_prefix}/lib/firewalld/zones/libvirt.xml
%{_prefix}/lib/firewalld/zones/libvirt-routed.xml
%{_prefix}/lib/firewalld/policies/libvirt-routed-in.xml
%{_prefix}/lib/firewalld/policies/libvirt-routed-out.xml
%{_prefix}/lib/firewalld/policies/libvirt-to-host.xml
%endif

%files daemon-driver-nodedev
%config(noreplace) %{_sysconfdir}/libvirt/virtnodedevd.conf
%{_datadir}/augeas/lenses/virtnodedevd.aug
%{_datadir}/augeas/lenses/tests/test_virtnodedevd.aug
%{_unitdir}/virtnodedevd.service
%{_unitdir}/virtnodedevd.socket
%{_unitdir}/virtnodedevd-ro.socket
%{_unitdir}/virtnodedevd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtnodedevd
%ghost %dir %{_rundir}/libvirt/nodedev/
%{_libdir}/libvirt/connection-driver/libvirt_driver_nodedev.so
%{_mandir}/man8/virtnodedevd.8*

%files daemon-driver-nwfilter
%config(noreplace) %{_sysconfdir}/libvirt/virtnwfilterd.conf
%{_datadir}/augeas/lenses/virtnwfilterd.aug
%{_datadir}/augeas/lenses/tests/test_virtnwfilterd.aug
%{_unitdir}/virtnwfilterd.service
%{_unitdir}/virtnwfilterd.socket
%{_unitdir}/virtnwfilterd-ro.socket
%{_unitdir}/virtnwfilterd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtnwfilterd
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/nwfilter/
%ghost %dir %{_rundir}/libvirt/network/
%ghost %dir %{_rundir}/libvirt/nwfilter-binding/
%ghost %dir %{_rundir}/libvirt/nwfilter/
%{_libdir}/libvirt/connection-driver/libvirt_driver_nwfilter.so
%{_mandir}/man8/virtnwfilterd.8*

%files daemon-driver-secret
%config(noreplace) %{_sysconfdir}/libvirt/virtsecretd.conf
%{_datadir}/augeas/lenses/virtsecretd.aug
%{_datadir}/augeas/lenses/tests/test_virtsecretd.aug
%{_unitdir}/virtsecretd.service
%{_unitdir}/virtsecretd.socket
%{_unitdir}/virtsecretd-ro.socket
%{_unitdir}/virtsecretd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtsecretd
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/secrets/
%ghost %dir %{_rundir}/libvirt/secrets/
%{_libdir}/libvirt/connection-driver/libvirt_driver_secret.so
%{_mandir}/man8/virtsecretd.8*

%files daemon-driver-storage

%files daemon-driver-storage-core
%config(noreplace) %{_sysconfdir}/libvirt/virtstoraged.conf
%{_datadir}/augeas/lenses/virtstoraged.aug
%{_datadir}/augeas/lenses/tests/test_virtstoraged.aug
%{_unitdir}/virtstoraged.service
%{_unitdir}/virtstoraged.socket
%{_unitdir}/virtstoraged-ro.socket
%{_unitdir}/virtstoraged-admin.socket
%attr(0755, root, root) %{_sbindir}/virtstoraged
%attr(0755, root, root) %{_libexecdir}/libvirt_parthelper
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/storage/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/storage/autostart/
%ghost %dir %{_rundir}/libvirt/storage/
%{_libdir}/libvirt/connection-driver/libvirt_driver_storage.so
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_fs.so
%{_libdir}/libvirt/storage-file/libvirt_storage_file_fs.so
%{_mandir}/man8/virtstoraged.8*

%files daemon-driver-storage-disk
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_disk.so

%files daemon-driver-storage-logical
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_logical.so

%files daemon-driver-storage-scsi
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_scsi.so

%files daemon-driver-storage-iscsi
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_iscsi.so

%if %{with_storage_iscsi_direct}
%files daemon-driver-storage-iscsi-direct
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_iscsi-direct.so
%endif

%files daemon-driver-storage-mpath
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_mpath.so

%if %{with_storage_gluster}
%files daemon-driver-storage-gluster
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_gluster.so
%{_libdir}/libvirt/storage-file/libvirt_storage_file_gluster.so
%endif

%if %{with_storage_rbd}
%files daemon-driver-storage-rbd
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_rbd.so
%endif

%if %{with_storage_zfs}
%files daemon-driver-storage-zfs
%{_libdir}/libvirt/storage-backend/libvirt_storage_backend_zfs.so
%endif

%if %{with_qemu}
%files daemon-driver-qemu
%config(noreplace) %{_sysconfdir}/libvirt/virtqemud.conf
%config(noreplace) %{_prefix}/lib/sysctl.d/60-qemu-postcopy-migration.conf
%{_datadir}/augeas/lenses/virtqemud.aug
%{_datadir}/augeas/lenses/tests/test_virtqemud.aug
%{_unitdir}/virtqemud.service
%{_unitdir}/virtqemud.socket
%{_unitdir}/virtqemud-ro.socket
%{_unitdir}/virtqemud-admin.socket
%attr(0755, root, root) %{_sbindir}/virtqemud
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/autostart/
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/qemu/
%config(noreplace) %{_sysconfdir}/libvirt/qemu.conf
%config(noreplace) %{_sysconfdir}/libvirt/qemu-lockd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.qemu
%ghost %dir %{_rundir}/libvirt/qemu/
%ghost %dir %{_rundir}/libvirt/qemu/dbus/
%ghost %dir %{_rundir}/libvirt/qemu/passt/
%ghost %dir %{_rundir}/libvirt/qemu/slirp/
%ghost %dir %{_rundir}/libvirt/qemu/swtpm/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/channel/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/channel/target/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/checkpoint/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/dump/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/nvram/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/ram/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/save/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/snapshot/
%dir %attr(0750, root, root) %{_localstatedir}/cache/libvirt/qemu/
%{_datadir}/augeas/lenses/libvirtd_qemu.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%{_libdir}/libvirt/connection-driver/libvirt_driver_qemu.so
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/swtpm/
%dir %attr(0730, tss, tss) %{_localstatedir}/log/swtpm/libvirt/qemu/
%{_bindir}/virt-qemu-run
%{_mandir}/man1/virt-qemu-run.1*
%{_mandir}/man8/virtqemud.8*
%endif

%if %{with_lxc}
%files daemon-driver-lxc
%config(noreplace) %{_sysconfdir}/libvirt/virtlxcd.conf
%{_datadir}/augeas/lenses/virtlxcd.aug
%{_datadir}/augeas/lenses/tests/test_virtlxcd.aug
%{_unitdir}/virtlxcd.service
%{_unitdir}/virtlxcd.socket
%{_unitdir}/virtlxcd-ro.socket
%{_unitdir}/virtlxcd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtlxcd
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/lxc/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/lxc/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/lxc/autostart/
%config(noreplace) %{_sysconfdir}/libvirt/lxc.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.lxc
%ghost %dir %{_rundir}/libvirt/lxc/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/lxc/
%{_datadir}/augeas/lenses/libvirtd_lxc.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%attr(0755, root, root) %{_libexecdir}/libvirt_lxc
%{_libdir}/libvirt/connection-driver/libvirt_driver_lxc.so
%{_mandir}/man8/virtlxcd.8*
%endif

%if %{with_libxl}
%files daemon-driver-libxl
%config(noreplace) %{_sysconfdir}/libvirt/virtxend.conf
%{_datadir}/augeas/lenses/virtxend.aug
%{_datadir}/augeas/lenses/tests/test_virtxend.aug
%{_unitdir}/virtxend.service
%{_unitdir}/virtxend.socket
%{_unitdir}/virtxend-ro.socket
%{_unitdir}/virtxend-admin.socket
%attr(0755, root, root) %{_sbindir}/virtxend
%config(noreplace) %{_sysconfdir}/libvirt/libxl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl-lockd.conf
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/libxl/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/libxl/autostart/
%{_datadir}/augeas/lenses/libvirtd_libxl.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/libxl/
%ghost %dir %{_rundir}/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/channel/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/channel/target/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/dump/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/save/
%{_libdir}/libvirt/connection-driver/libvirt_driver_libxl.so
%{_mandir}/man8/virtxend.8*
%endif

%if %{with_vbox}
%files daemon-driver-vbox
%config(noreplace) %{_sysconfdir}/libvirt/virtvboxd.conf
%{_datadir}/augeas/lenses/virtvboxd.aug
%{_datadir}/augeas/lenses/tests/test_virtvboxd.aug
%{_unitdir}/virtvboxd.service
%{_unitdir}/virtvboxd.socket
%{_unitdir}/virtvboxd-ro.socket
%{_unitdir}/virtvboxd-admin.socket
%attr(0755, root, root) %{_sbindir}/virtvboxd
%{_libdir}/libvirt/connection-driver/libvirt_driver_vbox.so
%{_mandir}/man8/virtvboxd.8*
%endif

%if %{with_qemu_tcg}
%files daemon-qemu
%endif

%if %{with_qemu_kvm}
%files daemon-kvm
%endif

%if %{with_lxc}
%files daemon-lxc
%endif

%if %{with_libxl}
%files daemon-xen
%endif

%if %{with_vbox}
%files daemon-vbox
%endif

%if %{with_sanlock}
%files lock-sanlock
    %if %{with_qemu}
%config(noreplace) %{_sysconfdir}/libvirt/qemu-sanlock.conf
    %endif
    %if %{with_libxl}
%config(noreplace) %{_sysconfdir}/libvirt/libxl-sanlock.conf
    %endif
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/sanlock.so
%{_datadir}/augeas/lenses/libvirt_sanlock.aug
%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%dir %attr(0770, root, sanlock) %{_localstatedir}/lib/libvirt/sanlock
%{_sbindir}/virt-sanlock-cleanup
%{_mandir}/man8/virt-sanlock-cleanup.8*
%attr(0755, root, root) %{_libexecdir}/libvirt_sanlock_helper
%endif

%files client
%{_mandir}/man1/virsh.1*
%{_mandir}/man1/virt-xml-validate.1*
%{_mandir}/man1/virt-pki-query-dn.1*
%{_mandir}/man1/virt-pki-validate.1*
%{_mandir}/man7/virkey*.7*
%{_bindir}/virsh
%{_bindir}/virt-xml-validate
%{_bindir}/virt-pki-query-dn
%{_bindir}/virt-pki-validate
%{_datadir}/bash-completion/completions/virsh

%if %{with_qemu}
%files client-qemu
#%{_mandir}/man1/virt-qemu-qmp-proxy.1*
#%{_mandir}/man1/virt-qemu-sev-validate.1*
#%{_bindir}/virt-qemu-qmp-proxy
#%{_bindir}/virt-qemu-sev-validate
%endif

%files libs -f %{name}.lang
%license COPYING COPYING.LESSER
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/
%config(noreplace) %{_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{_sysconfdir}/libvirt/libvirt-admin.conf
%{_libdir}/libvirt.so.*
%{_libdir}/libvirt-qemu.so.*
%{_libdir}/libvirt-lxc.so.*
%{_libdir}/libvirt-admin.so.*
%dir %{_datadir}/libvirt/
%dir %{_datadir}/libvirt/schemas/
%{_datadir}/systemtap/tapset/libvirt_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_functions.stp
%if %{with_qemu}
%{_datadir}/systemtap/tapset/libvirt_qemu_probes*.stp
%endif
%{_datadir}/libvirt/schemas/*.rng
%{_datadir}/libvirt/cpu_map/*.xml
%{_datadir}/libvirt/test-screenshot.png

%if %{with_wireshark}
%files wireshark
%{wireshark_plugindir}/libvirt.so
%endif

%files nss
%{_libdir}/libnss_libvirt.so.2
%{_libdir}/libnss_libvirt_guest.so.2

%if %{with_lxc}
%files login-shell
%attr(4750, root, virtlogin) %{_bindir}/virt-login-shell
%{_libexecdir}/virt-login-shell-helper
%config(noreplace) %{_sysconfdir}/libvirt/virt-login-shell.conf
%{_mandir}/man1/virt-login-shell.1*
%endif

%files devel
%{_libdir}/libvirt.so
%{_libdir}/libvirt-admin.so
%{_libdir}/libvirt-qemu.so
%{_libdir}/libvirt-lxc.so
%dir %{_includedir}/libvirt
%{_includedir}/libvirt/virterror.h
%{_includedir}/libvirt/libvirt.h
%{_includedir}/libvirt/libvirt-admin.h
%{_includedir}/libvirt/libvirt-common.h
%{_includedir}/libvirt/libvirt-domain.h
%{_includedir}/libvirt/libvirt-domain-checkpoint.h
%{_includedir}/libvirt/libvirt-domain-snapshot.h
%{_includedir}/libvirt/libvirt-event.h
%{_includedir}/libvirt/libvirt-host.h
%{_includedir}/libvirt/libvirt-interface.h
%{_includedir}/libvirt/libvirt-network.h
%{_includedir}/libvirt/libvirt-nodedev.h
%{_includedir}/libvirt/libvirt-nwfilter.h
%{_includedir}/libvirt/libvirt-secret.h
%{_includedir}/libvirt/libvirt-storage.h
%{_includedir}/libvirt/libvirt-stream.h
%{_includedir}/libvirt/libvirt-qemu.h
%{_includedir}/libvirt/libvirt-lxc.h
%{_libdir}/pkgconfig/libvirt.pc
%{_libdir}/pkgconfig/libvirt-admin.pc
%{_libdir}/pkgconfig/libvirt-qemu.pc
%{_libdir}/pkgconfig/libvirt-lxc.pc
%dir %{_datadir}/libvirt/api/
%{_datadir}/libvirt/api/libvirt-api.xml
%{_datadir}/libvirt/api/libvirt-admin-api.xml
%{_datadir}/libvirt/api/libvirt-qemu-api.xml
%{_datadir}/libvirt/api/libvirt-lxc-api.xml

%if %{with_mingw}
%files -n mingw32-libvirt -f mingw32-libvirt.lang
%dir %{mingw32_sysconfdir}/libvirt/
%config(noreplace) %{mingw32_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{mingw32_sysconfdir}/libvirt/libvirt-admin.conf
%{mingw32_bindir}/libvirt-0.dll
%{mingw32_bindir}/virsh.exe
%{mingw32_bindir}/virt-admin.exe
%{mingw32_bindir}/virt-xml-validate
%{mingw32_bindir}/virt-pki-query-dn.exe
%{mingw32_bindir}/virt-pki-validate
%{mingw32_bindir}/libvirt-lxc-0.dll
%{mingw32_bindir}/libvirt-qemu-0.dll
%{mingw32_bindir}/libvirt-admin-0.dll
%{mingw32_libdir}/libvirt.dll.a
%{mingw32_libdir}/pkgconfig/libvirt.pc
%{mingw32_libdir}/pkgconfig/libvirt-qemu.pc
%{mingw32_libdir}/pkgconfig/libvirt-lxc.pc
%{mingw32_libdir}/pkgconfig/libvirt-admin.pc
%{mingw32_libdir}/libvirt-lxc.dll.a
%{mingw32_libdir}/libvirt-qemu.dll.a
%{mingw32_libdir}/libvirt-admin.dll.a
%dir %{mingw32_datadir}/libvirt/
%dir %{mingw32_datadir}/libvirt/schemas/
%{mingw32_datadir}/libvirt/schemas/*.rng
%dir %{mingw32_datadir}/libvirt/api/
%{mingw32_datadir}/libvirt/api/libvirt-api.xml
%{mingw32_datadir}/libvirt/api/libvirt-lxc-api.xml
%{mingw32_datadir}/libvirt/api/libvirt-qemu-api.xml
%{mingw32_datadir}/libvirt/api/libvirt-admin-api.xml
%{mingw32_datadir}/libvirt/cpu_map/*.xml
%{mingw32_datadir}/libvirt/test-screenshot.png
%dir %{mingw32_includedir}/libvirt
%{mingw32_includedir}/libvirt/libvirt.h
%{mingw32_includedir}/libvirt/libvirt-common.h
%{mingw32_includedir}/libvirt/libvirt-domain.h
%{mingw32_includedir}/libvirt/libvirt-domain-checkpoint.h
%{mingw32_includedir}/libvirt/libvirt-domain-snapshot.h
%{mingw32_includedir}/libvirt/libvirt-event.h
%{mingw32_includedir}/libvirt/libvirt-host.h
%{mingw32_includedir}/libvirt/libvirt-interface.h
%{mingw32_includedir}/libvirt/libvirt-network.h
%{mingw32_includedir}/libvirt/libvirt-nodedev.h
%{mingw32_includedir}/libvirt/libvirt-nwfilter.h
%{mingw32_includedir}/libvirt/libvirt-secret.h
%{mingw32_includedir}/libvirt/libvirt-storage.h
%{mingw32_includedir}/libvirt/libvirt-stream.h
%{mingw32_includedir}/libvirt/virterror.h
%{mingw32_includedir}/libvirt/libvirt-lxc.h
%{mingw32_includedir}/libvirt/libvirt-qemu.h
%{mingw32_includedir}/libvirt/libvirt-admin.h
%{mingw32_mandir}/man1/virsh.1*
%{mingw32_mandir}/man1/virt-admin.1*
%{mingw32_mandir}/man1/virt-xml-validate.1*
%{mingw32_mandir}/man1/virt-pki-query-dn.1*
%{mingw32_mandir}/man1/virt-pki-validate.1*
%{mingw32_mandir}/man7/virkey*.7*

%files -n mingw64-libvirt -f mingw64-libvirt.lang
%dir %{mingw64_sysconfdir}/libvirt/
%config(noreplace) %{mingw64_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{mingw64_sysconfdir}/libvirt/libvirt-admin.conf
%{mingw64_bindir}/libvirt-0.dll
%{mingw64_bindir}/virsh.exe
%{mingw64_bindir}/virt-admin.exe
%{mingw64_bindir}/virt-xml-validate
%{mingw64_bindir}/virt-pki-query-dn.exe
%{mingw64_bindir}/virt-pki-validate
%{mingw64_bindir}/libvirt-lxc-0.dll
%{mingw64_bindir}/libvirt-qemu-0.dll
%{mingw64_bindir}/libvirt-admin-0.dll
%{mingw64_libdir}/libvirt.dll.a
%{mingw64_libdir}/pkgconfig/libvirt.pc
%{mingw64_libdir}/pkgconfig/libvirt-qemu.pc
%{mingw64_libdir}/pkgconfig/libvirt-lxc.pc
%{mingw64_libdir}/pkgconfig/libvirt-admin.pc
%{mingw64_libdir}/libvirt-lxc.dll.a
%{mingw64_libdir}/libvirt-qemu.dll.a
%{mingw64_libdir}/libvirt-admin.dll.a
%dir %{mingw64_datadir}/libvirt/
%dir %{mingw64_datadir}/libvirt/schemas/
%{mingw64_datadir}/libvirt/schemas/*.rng
%dir %{mingw64_datadir}/libvirt/api/
%{mingw64_datadir}/libvirt/api/libvirt-api.xml
%{mingw64_datadir}/libvirt/api/libvirt-lxc-api.xml
%{mingw64_datadir}/libvirt/api/libvirt-qemu-api.xml
%{mingw64_datadir}/libvirt/api/libvirt-admin-api.xml
%{mingw64_datadir}/libvirt/cpu_map/*.xml
%{mingw64_datadir}/libvirt/test-screenshot.png
%dir %{mingw64_includedir}/libvirt
%{mingw64_includedir}/libvirt/libvirt.h
%{mingw64_includedir}/libvirt/libvirt-common.h
%{mingw64_includedir}/libvirt/libvirt-domain.h
%{mingw64_includedir}/libvirt/libvirt-domain-checkpoint.h
%{mingw64_includedir}/libvirt/libvirt-domain-snapshot.h
%{mingw64_includedir}/libvirt/libvirt-event.h
%{mingw64_includedir}/libvirt/libvirt-host.h
%{mingw64_includedir}/libvirt/libvirt-interface.h
%{mingw64_includedir}/libvirt/libvirt-network.h
%{mingw64_includedir}/libvirt/libvirt-nodedev.h
%{mingw64_includedir}/libvirt/libvirt-nwfilter.h
%{mingw64_includedir}/libvirt/libvirt-secret.h
%{mingw64_includedir}/libvirt/libvirt-storage.h
%{mingw64_includedir}/libvirt/libvirt-stream.h
%{mingw64_includedir}/libvirt/virterror.h
%{mingw64_includedir}/libvirt/libvirt-lxc.h
%{mingw64_includedir}/libvirt/libvirt-qemu.h
%{mingw64_includedir}/libvirt/libvirt-admin.h
%{mingw64_mandir}/man1/virsh.1*
%{mingw64_mandir}/man1/virt-admin.1*
%{mingw64_mandir}/man1/virt-xml-validate.1*
%{mingw64_mandir}/man1/virt-pki-query-dn.1*
%{mingw64_mandir}/man1/virt-pki-validate.1*
%{mingw64_mandir}/man7/virkey*.7*
%endif

%changelog
* Fri Apr 14 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-10.1.el9_2
- virnuma: Move virNumaNodesetToCPUset() out of WITH_NUMACTL (rhbz#2185039)
- virnuma: Introduce virNumaCPUSetToNodeset() (rhbz#2185039)
- virnumamock: Introduce virNumaGetNodeOfCPU() mock (rhbz#2185039)
- qemuxml2argvtest: Use virnuma mock (rhbz#2185039)
- qemuxml2argvdata: Adjust maximum NUMA node used (rhbz#2185039)
- qemuxml2argvdata: Extend vCPUs placement in memory-hotplug-dimm-addr.xml (rhbz#2185039)
- qemuxml2argvmock: Drop virNuma* mocks (rhbz#2185039)
- qemu: Move cpuset preference evaluation into a separate function (rhbz#2185039)
- qemu: Fix qemuDomainGetEmulatorPinInfo() (rhbz#2185039)
- qemuBuildMemoryBackendProps: Join two conditions (rhbz#2185039)
- qemu: Add @nodemaskRet argument to qemuBuildMemoryBackendProps() (rhbz#2185039)
- qemu: Add @nodemask argument to qemuBuildThreadContextProps() (rhbz#2185039)
- qemuBuildThreadContextProps: Prune .node-affinity wrt <emulatorpin/> (rhbz#2185039)
- docs: Document memory allocation and emulator pinning limitation (rhbz#2185039)
- conf: Fix migration in some firmware autoselection scenarios (rhbz#2186383)

* Wed Mar 22 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-10
- po: Updated translation files from upstream (rhbz#2139664)

* Thu Mar 16 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-9
- util: add an API to retrieve the resolved path to a virCommand's binary (rhbz#2172267)
- security: make args to virSecuritySELinuxContextAddRange() const (rhbz#2172267)
- security: make it possible to set SELinux label of child process from its binary (rhbz#2172267)
- qemu: set SELinux label of passt process to its own binary's label (rhbz#2172267)
- rpm: Recommend passt-selinux (rhbz#2172267)

* Fri Mar 10 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-8
- docs: Fix examples in virt-qemu-sev-validate man page (rhbz#2172347)
- docs: refer to --firmware instead of --loader (rhbz#2172347)
- rpm: add missing deps for the virt-qemu-sev-validate (rhbz#2172347)
- docs/kbase: fix example for SEV validation (rhbz#2172347)
- qemu_passt: Report error when getting passt PID failed (rhbz#2169244)
- qemu_passt: Avoid double daemonizing passt (rhbz#2169244)
- qemu_passt: Report passt's error on failed start (rhbz#2169244)
- qemu_passt: Deduplicate passt killing code (rhbz#2169244)
- qemu_passt: Let passt write the PID file (rhbz#2169244)
- qemu_passt: Remove passt socket file on exit (rhbz#2169244)
- tests: qemucapabilitiesdata: Update for the qemu-8.0 development cycle (rhbz#2172098)
- qemu: capabilities: Introduce QEMU_CAPS_NETDEV_STREAM_RECONNECT (rhbz#2172098)
- qemu: add reconnect=5 to passt qemu commandline options when available (rhbz#2172098)
- qemu: respond to NETDEV_STREAM_DISCONNECTED event (rhbz#2172098)
- qemu: domain: Fix logic when tainting domain (rhbz#2174446)
- qemu: agent: Make fetching of 'can-offline' member from 'guest-query-vcpus' optional (rhbz#2174446)
- qemu: validate: Fix logic for validating presence of the HPET timer (rhbz#2175813)

* Wed Feb 22 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-7
- qemu_snapshot: remove memory snapshot when deleting external snapshot (rhbz#2170826)
- qemu_snapshot: refactor qemuSnapshotDeleteExternalPrepare (rhbz#2170826)

* Fri Feb 17 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-6
- rpc: client: Don't check return value of virNetMessageNew (rhbz#2145188)
- rpc: Don't warn about "max_client_requests" in single-threaded daemons (rhbz#2145188)

* Mon Feb 13 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-5
- qemu_extdevice: Do cleanup host only for VIR_DOMAIN_TPM_TYPE_EMULATOR (rhbz#2168762)
- qemu: blockjob: Handle 'pending' blockjob state only when we need it (rhbz#2168769)

* Thu Feb  9 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-4
- qemuProcessStop: Fix detection of outgoing migration for external devices (rhbz#2161557)
- qemuExtTPMStop: Restore TPM state label more often (rhbz#2161557)
- qemuProcessLaunch: Tighten rules for external devices wrt incoming migration (rhbz#2161557)
- qemu_process: Produce better debug message wrt domain namespaces (rhbz#2167302)
- qemu_namespace: Deal with nested mounts when umount()-ing /dev (rhbz#2167302)
- qemuProcessRefreshDisks: Don't skip filling of disk information if tray state didn't change (rhbz#2166411)

* Wed Feb  1 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-3
- src: Don't use virReportSystemError() on virProcessGetStatInfo() failure (rhbz#2148266)
- qemu: Provide virDomainGetCPUStats() implementation for session connection (rhbz#2148266)
- virsh: Make domif-setlink work more than once (rhbz#2165466)
- qemu_fd: Remove declaration for 'qemuFDPassNewDirect' (rhbz#2040272)
- qemuStorageSourcePrivateDataFormat: Rename 'tmp' to 'objectsChildBuf' (rhbz#2040272)
- qemu: command: Handle FD passing commandline via qemuBuildBlockStorageSourceAttachDataCommandline (rhbz#2040272)
- qemuFDPassTransferCommand: Mark that FD was passed (rhbz#2040272)
- qemu: fd: Add helpers allowing storing FD set data in status XML (rhbz#2040272)
- qemu: domain: Store fdset ID for disks passed to qemu via FD (rhbz#2040272)
- qemu: block: Properly handle FD-passed disk hot-(un-)plug (rhbz#2040272)

* Wed Jan 25 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-2
- vircgroupv2: fix cpu.weight limits check (rhbz#2037998)
- domain_validate: drop cpu.shares cgroup check (rhbz#2037998)
- docs: document correct cpu shares limits with both cgroups v1 and v2 (rhbz#2037998)
- qemu_interface: Fix managed='no' case when creating an ethernet interface (rhbz#2144738)
- conf: clarify some external TPM error messages (rhbz#2063723)
- qemu: hotplug: Remove legacy quirk for 'dimm' address generation (rhbz#2158701)
- qemu: alias: Remove 'oldAlias' argument of qemuAssignDeviceMemoryAlias (rhbz#2158701)
- qemu: Remove 'memAliasOrderMismatch' field from VM private data (rhbz#2158701)
- rpc: Fix error message in virNetServerSetClientLimits (rhbz#2033879)

* Mon Jan 16 2023 Jiri Denemark <jdenemar@redhat.com> - 9.0.0-1
- Rebased to libvirt-9.0.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2151064, rhbz#1874163, rhbz#2130192, rhbz#2111948, rhbz#1824722
    rhbz#2150455, rhbz#2063723, rhbz#1717611, rhbz#2160448, rhbz#2151869
    rhbz#2040272, rhbz#2144738, rhbz#2159851, rhbz#2156289, rhbz#2033879
    rhbz#1820437, rhbz#2151202

* Tue Dec  6 2022 Jiri Denemark <jdenemar@redhat.com> - 8.10.0-2
- qemu_process: Document qemuProcessPrepare{Domain,Host}() order (rhbz#2150760)
- qemu_extdevice: Init paths in qemuExtDevicesPrepareDomain() (rhbz#2150760)
- qemu_extdevice: Expose qemuExtDevicesInitPaths() (rhbz#2150760)
- qemu: Init ext devices paths on reconnect (rhbz#2150760)

* Thu Dec  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.10.0-1
- Rebased to libvirt-8.10.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2128993, rhbz#2143235, rhbz#2143840, rhbz#1874163, rhbz#2000075
    rhbz#2143838, rhbz#2104919, rhbz#2072204, rhbz#2137298

* Wed Nov  2 2022 Jiri Denemark <jdenemar@redhat.com> - 8.9.0-2
- RHEL: rpminspect: Disable abidiff inspection (rhbz#2124466)
- spec: Fix python3-libvirt requirement in client-qemu package (rhbz#2124466)

* Tue Nov  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.9.0-1
- Rebased to libvirt-8.9.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2074559, rhbz#2134009, rhbz#1777212, rhbz#2013523, rhbz#2114866
    rhbz#1964855

* Mon Oct  3 2022 Jiri Denemark <jdenemar@redhat.com> - 8.8.0-1
- Rebased to libvirt-8.8.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2122534, rhbz#2121262, rhbz#2130089, rhbz#2121276, rhbz#2121627
    rhbz#2125111, rhbz#2129239, rhbz#1964855, rhbz#2114866

* Tue Sep  6 2022 Jiri Denemark <jdenemar@redhat.com> - 8.7.0-1
- Rebased to libvirt-8.7.0 (rhbz#2124466)
- The rebase also fixes the following bugs:
    rhbz#2084046, rhbz#2108483, rhbz#2123371, rhbz#2101633, rhbz#1988211
    rhbz#2086677, rhbz#2103132, rhbz#2078805, rhbz#2111301, rhbz#2094641

* Thu Aug  4 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-5
- rpc: Pass OPENSSL_CONF through to ssh invocations (rhbz#2112348)

* Fri Jul 29 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-4
- qemu: Pass migration flags to qemuMigrationParamsApply (rhbz#2111070)
- qemu_migration_params: Replace qemuMigrationParamTypes array (rhbz#2111070)
- qemu_migration: Pass migParams to qemuMigrationSrcResume (rhbz#2111070)
- qemu_migration: Apply max-postcopy-bandwidth on post-copy resume (rhbz#2111070)
- qemu: Always assume support for QEMU_CAPS_MIGRATION_PARAM_XBZRLE_CACHE_SIZE (rhbz#2107892)
- qemu_migration: Store original migration params in status XML (rhbz#2107892)
- qemu_migration_params: Refactor qemuMigrationParamsApply (rhbz#2107892)
- qemu_migration_params: Refactor qemuMigrationParamsReset (rhbz#2107892)
- qemu_migration_params: Avoid deadlock in qemuMigrationParamsReset (rhbz#2107892)
- qemu: Restore original memory locking limit on reconnect (rhbz#2107424)
- qemu: Properly release job in qemuDomainSaveInternal (rhbz#1497907)
- qemu: don't call qemuMigrationSrcIsAllowedHostdev() from qemuMigrationDstPrepareFresh() (rhbz#1497907)

* Mon Jul 25 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-3
- qemu: introduce capability QEMU_CAPS_MIGRATION_BLOCKED_REASONS (rhbz#2092833)
- qemu: new function to retrieve migration blocker reasons from QEMU (rhbz#2092833)
- qemu: query QEMU for migration blockers before our own harcoded checks (rhbz#2092833)
- qemu: remove hardcoded migration fail for vDPA devices if we can ask QEMU (rhbz#2092833)
- qemu_migration: Use EnterMonitorAsync in qemuDomainGetMigrationBlockers (rhbz#2092833)
- qemu: don't try to query QEMU about migration blockers during offline migration (rhbz#2092833)
- qemu_migration: Acquire correct job in qemuMigrationSrcIsAllowed (rhbz#2092833)
- virsh: Require --xpath for *dumpxml (rhbz#2103524)
- qemu: skip hardcoded hostdev migration check if QEMU can do it for us (rhbz#1497907)

* Fri Jul 15 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-2
- domain_conf: Format <defaultiothread/> more often (rhbz#2059511)
- domain_conf: Format iothread IDs more often (rhbz#2059511)
- qemu: Make IOThread changing more robust (rhbz#2059511)
- qemuDomainSetIOThreadParams: Accept VIR_DOMAIN_AFFECT_CONFIG flag (rhbz#2059511)
- virsh: Implement --config for iothreadset (rhbz#2059511)
- docs: Document TPM portion of domcaps (rhbz#2103119)
- virtpm: Introduce TPM-1.2 and TPM-2.0 capabilieis (rhbz#2103119)
- domcaps: Introduce TPM backendVersion (rhbz#2103119)
- qemu: Report supported TPM version in domcaps (rhbz#2103119)
- vircpi: Add PCIe 5.0 and 6.0 link speeds (rhbz#2105231)

* Fri Jul  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.5.0-1
- Rebased to libvirt-8.5.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1475431, rhbz#2026765, rhbz#2059511, rhbz#2089431, rhbz#2102009

* Fri Jun 24 2022 Jiri Denemark <jdenemar@redhat.com> - 8.4.0-3
- qemu: fd: Fix monitor usage of qemuFDPassDirectGetPath (rhbz#2092856)

* Tue Jun 14 2022 Jiri Denemark <jdenemar@redhat.com> - 8.4.0-2
- Revert "RHEL: Fix virConnectGetMaxVcpus output" (rhbz#2095260)

* Thu Jun  2 2022 Jiri Denemark <jdenemar@redhat.com> - 8.4.0-1
- Rebased to libvirt-8.4.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#2057768, rhbz#2081981, rhbz#2035163, rhbz#2075837, rhbz#2082540
    rhbz#2075383

* Fri May  6 2022 Jiri Denemark <jdenemar@redhat.com> - 8.3.0-1
- Rebased to libvirt-8.3.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1653327, rhbz#2075765, rhbz#2075464, rhbz#2078274, rhbz#2070380
    rhbz#2073887, rhbz#2073867

* Fri Apr  1 2022 Jiri Denemark <jdenemar@redhat.com> - 8.2.0-1
- Rebased to libvirt-8.2.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1866400, rhbz#2065381, rhbz#2063903, rhbz#1901394, rhbz#2065399

* Fri Mar  4 2022 Jiri Denemark <jdenemar@redhat.com> - 8.1.0-1
- Rebased to libvirt-8.1.0 (rhbz#2060313)
- The rebase also fixes the following bugs:
    rhbz#1643868, rhbz#2045953, rhbz#1910856, rhbz#2051451, rhbz#1745868
    rhbz#2040548, rhbz#2041665, rhbz#1999372, rhbz#2038045, rhbz#2045959
    rhbz#2046024, rhbz#2040555, rhbz#2057067, rhbz#2037146, rhbz#2036300

* Thu Feb 24 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-5
- Make systemd unit ordering more robust (rhbz#1868537)
- util: Fix machined servicename (rhbz#1868537)

* Thu Feb 10 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-4
- qemu_command: Generate memory only after controllers (rhbz#2047271)
- qemu: Validate domain definition even on migration (rhbz#2048435)

* Wed Feb  2 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-3
- qemuDomainSetupDisk: Initialize 'targetPaths' (rhbz#2046170)

* Tue Jan 25 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-2
- build: Only install libvirt-guests when building libvirtd (rhbz#2042529)
- docs: Add man page for libvirt-guests (rhbz#2042529)
- remove sysconfig files (rhbz#2042529)
- spec: Run pre/post-install stuff on 'daemon-driver-storage-core' (rhbz#2025644)
- qemu: fix inactive snapshot revert (rhbz#2039136)
- Revert "report error when virProcessGetStatInfo() is unable to parse data" (rhbz#2043579)

* Fri Jan 14 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-1
- Rebased to libvirt-8.0.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2039246, rhbz#2039652, rhbz#2039651, rhbz#2039131

* Mon Jan 10 2022 Jiri Denemark <jdenemar@redhat.com> - 8.0.0-0rc1.1
- Rebased to libvirt-8.0.0-rc1 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2034539, rhbz#2027400, rhbz#1945420, rhbz#1851249, rhbz#2032410
    rhbz#2026812, rhbz#2032365, rhbz#2035888, rhbz#2036895, rhbz#2026537

* Wed Dec  1 2021 Jiri Denemark <jdenemar@redhat.com> - 7.10.0-1
- Rebased to libvirt-7.10.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2024098, rhbz#1964223, rhbz#2018488, rhbz#2021437, rhbz#2022589
    rhbz#2023605, rhbz#1431589, rhbz#2024435, rhbz#2016599, rhbz#1945501
    rhbz#2023674

* Fri Nov  5 2021 Jiri Denemark <jdenemar@redhat.com> - 7.9.0-1
- Rebased to libvirt-7.9.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2007659, rhbz#2014487, rhbz#1806856, rhbz#2014139, rhbz#1964223
    rhbz#2007168, rhbz#2012386, rhbz#2013573, rhbz#1897708

* Tue Oct  5 2021 Jiri Denemark <jdenemar@redhat.com> - 7.8.0-1
- Rebased to libvirt-7.8.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#1999420, rhbz#2002761, rhbz#1998920, rhbz#1986066, rhbz#1822891
    rhbz#2001627, rhbz#1819160, rhbz#2000861, rhbz#2003092

* Wed Sep 22 2021 Jiri Denemark <jdenemar@redhat.com> - 7.7.0-3
- virshDomainGetVcpuBitmap: Return bitmap when taking the fallback path (rhbz#2004429)

* Tue Sep 21 2021 Jiri Denemark <jdenemar@redhat.com> - 7.7.0-2
- Update gating.yaml by adding subject_type
- Revert "RHEL: spec: Do not enable modular daemons yet" (rhbz#1920012)

* Fri Sep 10 2021 Jiri Denemark <jdenemar@redhat.com> - 7.7.0-1
- Rebased to libvirt-7.7.0 (rhbz#2001507)
- The rebase also fixes the following bugs:
    rhbz#2001326, rhbz#2001391, rhbz#2001322, rhbz#2001389, rhbz#1967187
    rhbz#2001327, rhbz#1977155, rhbz#2001997, rhbz#2001323
- RHEL: spec: Do not enable modular daemons yet (rhbz#2001507)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 7.6.0-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Aug  4 2021 Jiri Denemark <jdenemar@redhat.com> - 7.6.0-1
- Rebased to libvirt-7.6.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1986509, rhbz#1984318, rhbz#1810661, rhbz#1977776, rhbz#1948433
    rhbz#1978526, rhbz#1976690

* Wed Jul 14 2021 Jiri Denemark <jdenemar@redhat.com> - 7.5.0-1
- Rebased to libvirt-7.5.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1949388, rhbz#1969354, rhbz#1970277, rhbz#1972145, rhbz#1973094
    rhbz#1975071, rhbz#1972468, rhbz#1975677

* Mon Jun  7 2021 Jiri Denemark <jdenemar@redhat.com> - 7.4.0-1
- Rebased to libvirt-7.4.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1960993

* Mon May 24 2021 Jiri Denemark <jdenemar@redhat.com> - 7.3.0-1
- Rebased to libvirt-7.3.0 (rhbz#1950948)
- The rebase also fixes the following bugs:
    rhbz#1898526, rhbz#1910617, rhbz#1910618, rhbz#1943392, rhbz#1946918
    rhbz#1947718, rhbz#1947720, rhbz#1947824, rhbz#1949342, rhbz#1950228
    rhbz#1950301, rhbz#1950601, rhbz#1950948, rhbz#1953939, rhbz#1958302
    rhbz#1962053
- RHEL: Enable usage of x-blockdev-reopen (rhbz#1953939)
- RHEL: Add gating.yaml for RHEL9 (rhbz#1950601)

* Thu Apr 22 2021 Jiri Denemark <jdenemar@redhat.com> - 7.0.0-6
- spec: Do not build qemu driver for Power on RHEL-9 (rhbz#1946529)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 7.0.0-5
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Feb 03 2021 Cole Robinson <aintdiscole@gmail.com> - 7.0.0-4
- Increase meson test timeout to fix builds on s390x copr

* Tue Feb 02 2021 Laine Stump <laine@redhat.com> - 7.0.0-3
- disable netcf in build

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 15 2021 Daniel P. Berrangé <berrange@redhat.com> - 7.0.0-1
- Rebase to 7.0.0 release

* Fri Dec 04 2020 Cole Robinson <aintdiscole@gmail.com> - 6.10.0-2.1
- Rebuild for wireshark soname bump

* Fri Dec 04 2020 Richard W.M. Jones <rjones@redhat.com> - 6.10.0-2
- Build libvirt-daemon-kvm for riscv64.

* Tue Dec 01 2020 Cole Robinson <crobinso@redhat.com> - 6.10.0-1
- Update to version 6.10.0

* Wed Nov  4 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.9.0-2
- Re-apply reverted fix for disabling glusterfs, curl, openswman and libiscsi

* Tue Nov 03 2020 Cole Robinson <crobinso@redhat.com> - 6.9.0-1
- Update to version 6.9.0

* Mon Nov  2 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-4
- Really fix meson option for disabling glusterfs
- Fix disabling curl, openswman and libiscsi

* Mon Nov  2 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-4
- Fix name of meson option for disabling glusterfs

* Fri Oct 30 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-3
- Fix stat() mocking for new glibc

* Wed Oct 28 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.8.0-2
- Remove obsolete bash_completion conditional
- Pass args to meson based on with_libssh/with_libssh2

* Thu Oct 01 2020 Cole Robinson <crobinso@redhat.com> - 6.8.0-1
- Update to version 6.8.0

* Fri Sep  4 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.7.0-2
- Fix QEMU start when KVM is not loaded (rhbz#1875327)

* Tue Sep 01 2020 Cole Robinson <crobinso@redhat.com> - 6.7.0-1
- Update to version 6.7.0

* Fri Aug 21 2020 Merlin Mathesius <mmathesi@redhat.com> - 6.6.0-3
- Fix so no platforms depend upon ceph for 32-bit architectures
- Include upstream patches to fix GCC 10 warnings

* Fri Aug 21 2020 Daniel P. Berrangé <berrange@redhat.com> - 6.6.0-2
- Fix creation of pools on non-btrfs (rhbz#1870197)

* Tue Aug 04 2020 Cole Robinson <crobinso@redhat.com> - 6.6.0-1
- Update to version 6.6.0

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 03 2020 Cole Robinson <crobinso@redhat.com> - 6.5.0-1
- Update to version 6.5.0

* Tue Jun 02 2020 Cole Robinson <crobinso@redhat.com> - 6.4.0-1
- Update to version 6.4.0

* Tue May 05 2020 Cole Robinson <crobinso@redhat.com> - 6.3.0-1
- Update to version 6.3.0

* Thu Apr 02 2020 Cole Robinson <crobinso@redhat.com> - 6.2.0-1
- Update to version 6.2.0

* Tue Mar 24 2020 Felipe Borges <feborges@redhat.com> - 6.1.0-2
- Check for disk type correctly in virDomainDiskTranslateSourcePool

* Wed Mar 04 2020 Cole Robinson <crobinso@redhat.com> - 6.1.0-1
- Update to version 6.1.0

* Tue Feb 25 2020 Cole Robinson <crobinso@redhat.com> - 6.0.0-3
- Rebuild for libiscsi soname bump

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jan 15 2020 Cole Robinson <crobinso@redhat.com> - 6.0.0-1
- Update to version 6.0.0
