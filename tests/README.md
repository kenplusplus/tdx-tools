
# TDX Tests

## 1. Overview

TDX tests are designed to cover basic acceptance tests, functionality, workload
and environment tests for TDX. It also provides tests for interoperability tests
with TDX and AMX. The tests implementation depends on PyCloudStack framework.
The tests execution should be on TDX enabled Linux platform with TDX-enabled kernel,
Qemu, Libvirt installed.

The tests can be categorized as following.

| Category         |        Tests         | Prerequisite |
|------------------|----------------------|--------------|
|    BAT           | test_vm_coexist      |              |
|    BAT           | test_tdx_guest_status|              |
|    BAT           | test_tdx_host_status |              |
|    BAT           | test_tdvm_lifecycle  |              |
|    BAT           | test_multiple_tdvms  |              |
| Environment      | test_tdvm_tsc        |              |
| Environment      | test_tdvm_network    |              |
| Environment      | test_max_cpu         |              |
| Lifecycle        | test_vm_shutdown_mode|              |
| Lifecycle        | test_vm_shutdown_qga |       1      |
| Lifecycle        | test_vm_reboot_qga   |       1      |
| Lifecycle        | test_acpi_reboot     |              |
| Lifecycle        | test_acpi_shutdown   |              |
| Interoperability | test_amx_docker_tf   |      2,4     |
| Interoperability | test_amx_vm_tf       |       5      |
| Workload         | test_workload_nginx  |      2,3     |
| Workload         | test_workload_redis  |      2,3     |
|                  |                      |              |

- Prerequisite: Please refer to corresponding items in section `Prerequisite of tests` below.

## 2. Prerequisite

### Enable TDX

Please make sure your Linux host has TDX enabled.

### Create Guest Image

A customized guest image is needed for tests.

For Ubuntu 22.04 guest image, please refer to [Ubuntu Guest Image](/build/ubuntu-22.04/guest-image/README.md).

For RHEL 8.x guest image, please refer to [RHEL8 Guest Image](/build/rhel-8/guest-image/README.md).

### Prepare Environment

- Install required packages:

  If your host distro is RHEL 8:

    ```
    sudo dnf install python3-virtualenv python3-libvirt libguestfs-devel libvirt-devel python3-devel gcc gcc-c++
    ```

  If your host distro is Ubuntu 22.04:

    ```
    sudo apt install python3-virtualenv python3-libvirt libguestfs-dev libvirt-dev python3-dev
    ```

- Make sure libvirt service is started. If not, start libvirt service.

     ```
    sudo systemctl status libvirtd
    sudo systemctl start libvirtd
    ```

- Setup environment:

    Run below command to setup the python environment

    ```
    cd tdx-tools/tests/
    source setupenv.sh
    ```

- Generate artifacts.yaml

    Please refer to tdx-tools/tests/artifacts.yaml.template and generate tdx-tools/tests/artifacts.yaml. Update `source`
    and `sha256sum` to indicate the location of guest image and guest kernel. 

    Example of using local files in artifacts.yaml

    ```
    latest-guest-image-ubuntu:
      source: file:///<file-path>/td-guest-ubuntu-22.04-test.qcow2
    latest-guest-kernel-ubuntu:
      source: file:///<file-path>/vmlinuz-jammy    
    ```

    Example of using remote files in artifacts.yaml

    ```
    latest-guest-image-ubuntu:
      source: http://<path>/td-guest-ubuntu-22.04-test.qcow2.tar.xz
      sha256sum: http://<path>/td-guest-ubuntu-22.04-test.qcow2.tar.xz.sha256sum 
    latest-guest-kernel-ubuntu:
      source: http://<path>/vmlinuz-jammy  
      sha256sum: http://<path>/vmlinuz-jammy.sha256sum 
    ```

- Generate keys

    Generate a pair of keys that will be used in test running.

    ```
    ssh-keygen
    ```

    The keys should be named "vm_ssh_test_key" and "vm_ssh_test_key.pub" and located under tdx-tools/tests/tests/

### Prerequisite of tests

Basic guest image is required for all the tests. Additional requirement to guest image exists for part of the tests.
Please check prerequisite of each test and take corresponding action as following.

- Prerequisite:
    1. Install Qemu guest agent in guest image
    2. Install docker in guest image
    3. For workload tests, make sure the latest docker image is in guest image
       test_workload_nginx - it needs docker image nginx:latest
       test_workload_redis - it needs docker image redis:latest
    4. Make sure docker image intel/intel-optimized-tensorflow-avx512:2.8.0 is in guest image
    5. Install intel-tensorflow-avx512 in guest image. Download DIEN_bf16 model and put it under /root in guest image.
       For ubuntu guest image
       
       ```
       cd /root/
       pip3 install intel-tensorflow-avx512==2.11.0
       wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v2_5_0/dien_bf16_pretrained_opt_model.pb
       wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v2_5_0/dien_fp32_static_rnn_graph.pb
       mkdir dien
       pushd dien
         # Download the datasets following steps in https://github.com/IntelAI/models/blob/master/benchmarks/recommendation/tensorflow/dien/inference/README.md#Datasets
       popd
       git clone https://github.com/IntelAI/models.git
       pushd models
       git checkout v2.5.0
       popd
       ```
       
       For rhel guest image, please upgrade python to python 3.8 first and run the commands above afterwards.
       

## Run Tests

- User can specify guest image OS with `-g`. Currently it supports `ubuntu` and `rhel`. Ubuntu guest image is used by default if `-g` is not specified.
If you want to use RHEL guest image, please use below command.

    ```
    sudo ./run.sh -g rhel -s all
    ```

- Run all tests:

  ```
  sudo ./run.sh -s all
  ```

- Run some case modules: `./run.sh -c <test_module1> -c <test_module2>`

  For example,

  ```
  ./run.sh -c tests/test_tdvm_lifecycle.py
  ```

- Run specific cases: `./run.sh -c <test_module1> -c <test_module1>::<test_name>`

  For example,

  ```
  ./run.sh -c tests/test_tdvm_lifecycle.py -c tests/test_vm_coexist.py
  ```
