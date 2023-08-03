%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       intel-mvp-amber-cli
Version:    2023ww21
Release:    mvp5
Summary:    Migration for 64-bit virtual machines supporting trusted domains
Group:      Applications/Emulators
License:    BSD
URL:        https://github.com/intel/amber-client

Source0: amber-cli.tar.gz

BuildRequires:  golang
BuildRequires:  libtdx-attest-devel = 1.17.100.4-1.el8

Requires:  golang
Requires:  libtdx-attest-devel = 1.17.100.4-1.el8

%description
Go TDX CLI for integrating with Intel Project Amber V1 API.

%prep
%setup -q -n amber-cli

%build
make -C amber-cli-tdx cli

%install
mkdir -p %{buildroot}/usr/bin/
cp amber-cli-tdx/amber-cli %{buildroot}/usr/bin/

%files
/usr/bin/amber-cli
