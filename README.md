# Intel&reg; TDX(Trust Domain Extensions) MVP Stack

## Overview

Intel&reg; Trust Domain Extensions(TDX) refers to an Intel technology that
extends Virtual Machine Extensions(VMX) and Multi-Key Total Memory
Encryption(MK-TME) with a new kind of virtual machine guest called a Trust
Domain(TD). A TD runs in a CPU mode that protects the confidentiality of its
memory contents and its CPU state from any other software, including the hosting
Virtual Machine Monitor (VMM). Please get more details from _[TDX White Papers and Specifications](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-trust-domain-extensions.html)_


## Components

Intel&reg; TDX(Trust Domain Extensions) MVP Stack includes the components in
below diagram:

![TDX Stack Architecture](doc/tdx_stack_arch.png)

| Name | Stack | Description |
| -- | -- | -- |
| [TDX Host Kernel](https://github.com/intel/tdx/tree/kvm) | IaaS Host| The modified kernel for baremetal server with TDX KVM patches |
| [TDX Qemu-KVM](https://github.com/intel/qemu-tdx) | IaaS Host | The modified Qemu VMM to support to create TDX guest VM |
| [TDX Libvirt](https://github.com/intel/libvirt-tdx) | IaaS Host | The modified libvirt to create TDX guest domain via Qemu |
| [TDVF](https://github.com/tianocore/edk2-staging/tree/TDVF) | IaaS Host | The modified OVMF(Open Source Virtual Firmware) to support TDX guest boot like page accept, TDX measurement |
| [TDX Guest Kernel](https://github.com/intel/tdx/tree/guest) | PaaS VM | The modified kernel for guest VM with TDX patches |
| [TDX Grub2](https://github.com/intel/grub-tdx) | VM Guest | The modified grub for guest VM to support TDX measurement |
| [TDX shim](https://github.com/intel/shim-tdx) | VM Guest | The modified shim for guest VM to support TDX measurement |


## Getting Started

### Build

TBD

### Test

TBD

### FAQ & BKM

- [How to check memory encryption for TDX guest](doc/mem_encryption_check.md)
- [How to debug a TDX guest via Qemu GDB server](doc/off_td_debug.md)
