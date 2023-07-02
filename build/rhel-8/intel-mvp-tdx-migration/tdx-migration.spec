%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       intel-mvp-tdx-migration
Version:    2023ww25.3
Release:    mvp6
Summary:    Migration for 64-bit virtual machines supporting trusted domains
Group:      Applications/Emulators
License:    BSD and OpenSSL and MIT
URL:        https://github.com/intel/MigTD

Source0: tdx-migration.tar.gz

BuildRequires:  llvm clang
BuildRequires:  pkgconf
BuildRequires:  wget
BuildRequires:  ocaml
BuildRequires:  ocaml-ocamlbuild

# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

# Use cargo nightly-2022-11-15 instead.
BuildConflicts: cargo

BuildArch:  noarch

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

if [[ $($HOME/.cargo/bin/cargo --version) =~ "1.67.0-nightly" ]]; then
    echo "Found Cargo 1.67.0-nightly in $HOME/.cargo/"
else
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup-init.sh
    chmod +x rustup-init.sh;./rustup-init.sh -y --profile minimal --default-toolchain nightly-2022-11-15
fi
source "$HOME/.cargo/env"
cargo install cargo-xbuild
rustup component add rust-src
./sh_script/preparation.sh
cargo image

%install
mkdir -p %{buildroot}/usr/share/td-migration
cp target/release/migtd.bin %{buildroot}/usr/share/td-migration

%files
/usr/share/td-migration/migtd.bin
