%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       vtpm-td
Version:    v0.3.0
Release:    mvp10
Summary:    Trust Domain (TD) based vTPM solution
Group:      Applications/Emulators
License:    BSD and OpenSSL and MIT
URL:        https://github.com/intel/vtpm-td

Source0: vtpm-td.tar.gz

BuildRequires: llvm clang
BuildRequires: pkgconf
BuildRequires: wget
BuildRequires: ocaml
BuildRequires: ocaml-ocamlbuild
BuildRequires: perl(Test::Harness), perl(Test::More), perl(Math::BigInt)
BuildRequires: perl(Module::Load::Conditional), perl(File::Temp)
BuildRequires: perl(Time::HiRes), perl(IPC::Cmd), perl(Pod::Html), perl(Digest::SHA)
BuildRequires: perl(FindBin), perl(lib), perl(File::Compare), perl(File::Copy), perl(bigint)

# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

%description
rust-vtpm-td is a Trust Domain (TD) based vTPM solution, which can support vTPM functionality with VMM out of TCB.

%prep
%setup -q -n vtpm-td

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

export CC=clang
export AR=llvm-ar
# build
sh_script/pre-build.sh
sh_script/build.sh

%install
mkdir -p %{buildroot}/usr/share/tdx-vtpm/
cp target/x86_64-unknown-none/release/vtpmtd.bin %{buildroot}/usr/share/tdx-vtpm

%files
/usr/share/tdx-vtpm/vtpmtd.bin
