"""
This module provide the case to test VM boot with max vCPU

"""

import logging
import psutil
import pytest
from pycloudstack.vmparam import VM_TYPE_LEGACY, VM_STATE_RUNNING, VM_TYPE_EFI, VM_TYPE_TD, VMSpec

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]

# Get host total cores and sockets, assign 80% vcpu and 80% memory to vm
total_core = psutil.cpu_count()
cores = int(total_core * 0.4)
memsize = int(psutil.virtual_memory().available / 1000 * 0.8)
vmspec = VMSpec(sockets=2, cores=cores, memsize=memsize)

def test_td_max_vcpu(vm_factory):
    """
    Test boot TD guest with max vcpu KVM supports
    """

    LOG.info("Create guest")
    inst = vm_factory.new_vm(VM_TYPE_TD, vmspec=vmspec, auto_start=True)

    assert inst.wait_for_state(VM_STATE_RUNNING), "Boot fail"
    assert inst.wait_for_ssh_ready(), "Boot timeout"

    # Destroy VM to release CPU resource
    inst.destroy()

def test_efi_max_vcpu(vm_factory):
    """
    Test boot TD guest with max vcpu KVM supports
    """

    LOG.info("Create guest")
    inst = vm_factory.new_vm(VM_TYPE_EFI, vmspec=vmspec, auto_start=True)

    assert inst.wait_for_state(VM_STATE_RUNNING), "Boot fail"
    assert inst.wait_for_ssh_ready(), "Boot timeout"

    # Destroy VM to release CPU resource
    inst.destroy()

def test_legacy_max_vcpu(vm_factory):
    """
    Test boot legacy guest with max vcpu KVM supports
    """

    LOG.info("Create guest")
    inst = vm_factory.new_vm(VM_TYPE_LEGACY, vmspec=vmspec, auto_start=True)

    assert inst.wait_for_state(VM_STATE_RUNNING), "Boot fail"
    assert inst.wait_for_ssh_ready(), "Boot timeout"

    # Destroy VM to release CPU resource
    inst.destroy()
