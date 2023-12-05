# Tests

## Prerequisites

The basic assumption is that you have a TDX enabled host and guest image.

e.g. If you want to run the test on Ubuntu, then you can follow the steps in [canonical/tdx: Intel confidential computing - TDX (github.com)](https://github.com/canonical/tdx)

And some dependencies are needed to be installed in the guest image:

1. qemu-guest-agent. It's needed by test_vm_shutdown_mode.py.

2. docker. It's needed by test_workload_nginx.py and test_workload_redis.py.

3. redis-cli. It's needed by test_workload_redis.py.

4. bombardier. It's needed by test_workload_nginx.py.



## How To Run

One quick example could be:

`source ./setupenv.sh`

`./run.sh -c tests/test_tdvm_lifecycle.py::test_tdvm_lifecycle_virsh_start_shutdown`

For more details, please reference [Whitepaper: Linux* Stacks for Intel® Trust Domain Extensions 1.5](https://www.intel.com/content/www/us/en/content-details/790888/whitepaper-linux-stacks-for-intel-trust-domain-extensions-1-5.html) section "3.5.3 Intel TDX Tests".
