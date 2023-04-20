# TD Migration

## 1. Overview

This feature is to meet the CSP who may want to relocate/migrate an executing Trust Domain (TD) from a source Trust Domain Extension (TDX) platform to a destination TDX platform in the cloud environment. Currently, td-migration only works on **TDX 1.5 (kernel-v6.2/tag 2023ww15 and later)**. Tags for TDX 1.0 do not support this feature. It also requires `MigTD` which is not included in tdx-tools yet. Please contact Intel sales rep to get MigTD before performing the following TD migration steps.

In this doc, the TD being migrated is called the source TD, and the TD created as a result of the migration is called the destination TD.

**Prerequisite**: Please install all attestation required components on both source and destination platform because pre-migration includes mutual attestation for MigTD. If pre-migration is successful, it means MigTD attestation pass. Please refer to
[TDX End to End Attestation](https://github.com/intel/tdx-tools/wiki/5.-TDX-End-to-End-Attestation) to setup attestation environment.

## 2. Single Host Test Steps

**NOTE**: each command needs one terminal, so please prepare 5 terminal tabs firstly or use tmux.

### 2.1 Create Migration TDs

The migration TDs are designed to evaluate potential migration source and target for adherence to the TD Migration Policy and exchange MSK(Migration session Key) from the source platform to the destination platform. Creating migration TDs is an additional workflow compared with live migration.

NOTE: the default installation path of `migtd.bin` is "/usr/share/td-migration/migtd.bin" (provided by intel-mvp-tdx-migration pkg)

```bash
# create the MigTD_src to bind with src user TD 
sudo ./mig-td.sh -t src

# create the MigTD_dst to bind with dst user TD 
sudo ./mig-td.sh -t dst
```

Use `-m` parameter to set the alternative path of migtd.bin.

```bash
sudo ./mig-td.sh -m path/to/migtd.bin -t src
```

If MigTD starts successfully, the console will display the below message.

```console
MigTD Version - 0.2.1
Loop to wait for request
```

### 2.2 Launch Source and Destination TDs

For live migration, it is a process that transfers source TD to destination TD. 

Before starting live migration, you can use direct boot or grub boot to launch both types of TDs.

- Direct Boot

NOTE: The default ROOT_PARTITION is `/dev/vda1`, which is for ubuntu guest TD. For RHEL, please add parameter `-r /dev/vda3`

```bash
# create the source TD
sudo ./user-td.sh -t src -i path/to/image -k path/to/kernel

# create the destiation TD
sudo ./user-td.sh -t dst -i path/to/image -k path/to/kernel
```

- GRUB Boot

```bash
# create the source TD
sudo ./user-td.sh -t src -i path/to/image -b grub

# create the destiation TD
sudo ./user-td.sh -t dst -i path/to/image -b grub
```

For attestation, you need to enable tdvmcall or vsock for TD to connect with QGS.

```bash
# tdvmcall
sudo ./user-td.sh -t src -i path/to/image -b grub -q tdvmcall
sudo ./user-td.sh -t dst -i path/to/image -b grub -q tdvmcall

# vsock
sudo ./user-td.sh -t src -i path/to/image -b grub -q vsock
sudo ./user-td.sh -t dst -i path/to/image -b grub -q vsock
```

### 2.3 Pre-Migration

Wait a while for source and destination TDs to be ready.

Before starting pre-migration, create a channel between source and destination side migration TDs.

```bash
sudo ./connect.sh
```

Check if it creates successfully.

```console
$ ps axu| grep socat
root      112608  0.0  0.0  27828  3072 pts/5    S    Mar22   0:00 socat TCP4-LISTEN:9009,reuseaddr VSOCK-LISTEN:1234,fork
root      112609  0.0  0.0  27828  3072 pts/5    S    Mar22   0:00 socat TCP4-CONNECT:127.0.0.1:9009,reuseaddr VSOCK-LISTEN:1235,fork
```

Start pre-migration.

```bash
sudo ./pre-mig.sh
```

Check pre-migrate status.

```console
$ dmesg
[110722.032798] kvm_intel: Pre-migration is done, userspace pid=368587
[110722.074132] kvm_intel: Pre-migration is done, userspace pid=368515
```

### 2.4 Live Migration

Start transferring TD's data from source to destination.

```bash
sudo ./mig-flow.sh
```

After migration is complete, you will see the following message and destination TD is ready.

```console
$ dmesg
[110983.886989] migration flow is done, userspace pid 397008
```

## 3.Cross Host Test Steps

**NOTE:** For cross-host live migration, you have to set up NFS server or use other ways to share the image/kernel for source TD and destination TD before starting the migration. (It means source TD and destination TD can access the shared image/kernel together)

### 3.1 Create Migration TDs

NOTE: the default installation path of `migtd.bin` is "/usr/share/td-migration/migtd.bin" (provided by intel-mvp-tdx-migration pkg)

```bash
# create the MigTD_src to bind with src user TD 
sudo ./mig-td.sh -t src

# create the MigTD_dst to bind with dst user TD 
sudo ./mig-td.sh -t dst
```

Use `-m` parameter to set the alternative path of migtd.bin.

```bash
sudo ./mig-td.sh -t src -m path/to/migtd.bin
```

If the migration TD starts successfully, the console will display the below message.

```console
MigTD Version - 0.2.1
Loop to wait for request
```

### 3.2 Launch Source and Destination TDs

Create source and destination TDs before starting live migration.

- Direct Boot

NOTE: The default ROOT_PARTITION is `/dev/vda1`, which is for ubuntu guest TD. For RHEL, please add parameter `-r /dev/vda3`

```bash
# create the source TD on source platform
sudo ./user-td.sh -t src -i path/to/image -k path/to/kernel

# create the destiation TD on destination platform
sudo ./user-td.sh -t dst -i path/to/image -k path/to/kernel
```

- GRUB Boot

```bash
# create the source TD on source platform
sudo ./user-td.sh -t src -i path/to/image -b grub

# create the destiation TD on destination platform
sudo ./user-td.sh -t dst -i path/to/image -b grub
```

Cross-host attestation is same as the Single-host, so please refer Section 2.2.

### 3.3 Pre-Migration

This step has a little difference with the single host live migration.

Create a channel between source and destination side migration TDs.

```bash
sudo ./connect.sh -t remote -i <DEST_IP>
```

Start Pre-Migration.

```bash
sudo ./pre-mig.sh -t remote -i <DEST_IP>
```

Check if pre-migrate is successful on both platforms.

```console
$ dmesg
[110722.032798] kvm_intel: Pre-migration is done, userspace pid=368587
```

### 3.4 Live Migration

```bash
sudo ./mig-flow.sh -i <dest-platform-ip>
```

After migration is complete, you will see the following message and destination TD is ready.

```console
$ dmesg
[110983.886989] migration flow is done, userspace pid 397008
```

## 4. Related Specification

1. [Intel® TDX Module Architecture Specification: TD
Migration](https://cdrdv2.intel.com/v1/dl/getContent/733578)
2. [Intel® TDX Migration TD Design Guide](https://cdrdv2.intel.com/v1/dl/getContent/733580)
