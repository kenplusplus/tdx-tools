%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       mig-td
Version:    v0.3.1
Release:    mvp12
Summary:    Migration for 64-bit virtual machines supporting trusted domains
Group:      Applications/Emulators
License:    BSD and OpenSSL and MIT
URL:        https://github.com/intel/MigTD.git

Source0: tdx-migration.tar.gz

BuildRequires:  llvm clang
BuildRequires:  pkgconf
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  wget
BuildRequires:  ocaml
BuildRequires:  ocaml-ocamlbuild
BuildRequires:  openssl-devel
BuildRequires:  perl(FindBin)

# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

Requires: socat >= 1.7.4

%description
Migration TD (MigTD) is used to evaluate potential migration sources and targets for
adherence to the TD Migration Policy, then securely transfer a Migration Session Key
from the source platform to the destination platform to migrate assets of a specific TD.

%prep
%setup -q -n migtd

# Done by %setup, but we do not use it for the auxiliary tarballs
chmod -Rf a+rX,u+w,g-w,o-w .

%build

# Github runner overrides to /github/home
user_id=$(id -u)
if [ "$user_id" -eq 0 ]; then
    export HOME=/root
fi

if [[ $($HOME/.cargo/bin/cargo --version) =~ "1.74.0-nightly" ]]; then
    echo "Found Cargo 1.74.0-nightly in $HOME/.cargo/"
else
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup-init.sh
    chmod +x rustup-init.sh;./rustup-init.sh -y --profile minimal --default-toolchain nightly-2023-08-28
fi
source "$HOME/.cargo/env"
cargo install cargo-xbuild
rustup component add rust-src
./sh_script/preparation.sh
export RUST_BACKTRACE=1
cargo image 
cargo image --no-default-features --features remote-attestation,stack-guard,virtio-serial -o target/release/migtd-serial.bin
cargo hash --image target/release/migtd.bin > ./migtd.servtd_info_hash
cargo hash --image target/release/migtd-serial.bin > ./migtd-serial.servtd_info_hash

%install
mkdir -p %{buildroot}/usr/share/td-migration
cp target/release/migtd.bin %{buildroot}/usr/share/td-migration
cp migtd.servtd_info_hash %{buildroot}/usr/share/td-migration
cp target/release/migtd-serial.bin %{buildroot}/usr/share/td-migration
cp migtd-serial.servtd_info_hash %{buildroot}/usr/share/td-migration

%files
/usr/share/td-migration/migtd.bin
/usr/share/td-migration/migtd.servtd_info_hash
/usr/share/td-migration/migtd-serial.bin
/usr/share/td-migration/migtd-serial.servtd_info_hash
