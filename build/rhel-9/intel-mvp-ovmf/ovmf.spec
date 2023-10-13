%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       ovmf
Version:    ww36.2
Release:    mvp17%{?dist}
Summary:    UEFI firmware for 64-bit virtual machines supporting trusted domains
Group:      Applications/Emulators
License:    BSD and OpenSSL and MIT
URL:        http://www.tianocore.org

Source0: mvp-tdx-ovmf.tar.gz

BuildRequires:  python3-devel
BuildRequires:  libuuid-devel
BuildRequires:  openssl-devel
BuildRequires:  /usr/bin/iasl
BuildRequires:  binutils gcc git gcc-c++ make

# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

# Only OVMF includes the Secure Boot feature, for which we need to separate out
# the UEFI shell.
BuildRequires:  dosfstools
BuildRequires:  mtools
BuildRequires:  xorriso

BuildArch:  noarch

# OVMF includes the Secure Boot feature; it has a builtin OpenSSL library.
Provides:   bundled(openssl) = 1.1.1g

%description
OVMF (Open Virtual Machine Firmware) is a project to enable UEFI support for
Virtual Machines. This package contains a sample 64-bit UEFI firmware for QEMU
and KVM supporting trusted domains.

%prep
%setup -q -n mvp-tdx-ovmf

# Done by %setup, but we do not use it for the auxiliary tarballs
chmod -Rf a+rX,u+w,g-w,o-w .

%build
export PYTHON_COMMAND=python3

make -C BaseTools
source ./edksetup.sh
build -p OvmfPkg/IntelTdx/IntelTdxX64.dsc \
      -a X64 -b DEBUG \
      -t GCC5 \
      -D DEBUG_ON_SERIAL_PORT=TRUE \
      -D SECURE_BOOT_ENABLE=TRUE \

build -p OvmfPkg/IntelTdx/IntelTdxX64.dsc \
      -a X64 -b RELEASE \
      -t GCC5 \
      -D DEBUG_ON_SERIAL_PORT=FALSE \
      -D SECURE_BOOT_ENABLE=TRUE \

%install
mkdir -p %{buildroot}/usr/share/qemu
cp Build/IntelTdx/DEBUG_GCC*/FV/OVMF.fd %{buildroot}/usr/share/qemu/OVMF.debug.fd
cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF.fd %{buildroot}/usr/share/qemu/
cp Build/IntelTdx/DEBUG_GCC*/FV/OVMF_CODE.fd %{buildroot}/usr/share/qemu/OVMF_CODE.debug.fd
cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF_CODE.fd %{buildroot}/usr/share/qemu/
cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF_VARS.fd %{buildroot}/usr/share/qemu/

%files
%license License.txt
/usr/share/qemu/OVMF.debug.fd
/usr/share/qemu/OVMF.fd
/usr/share/qemu/OVMF_CODE.debug.fd
/usr/share/qemu/OVMF_CODE.fd
/usr/share/qemu/OVMF_VARS.fd
