"""
Test network functionality within TD guest
"""

import logging
import pytest
from pycloudstack.vmparam import VM_TYPE_TD
from pycloudstack.cmdrunner import NativeCmdRunner

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]


def test_tdvm_wget(vm_factory, vm_ssh_pubkey, vm_ssh_key):
    """
    Test wget functionality within TD guest, the network could be NAT, bridget.
    """

    LOG.info("Create TD guest")
    vm_inst = vm_factory.new_vm(VM_TYPE_TD)

    # customize the VM image
    vm_inst.image.inject_root_ssh_key(vm_ssh_pubkey)

    # create and start VM instance
    vm_inst.create()
    vm_inst.start()
    assert vm_inst.wait_for_ssh_ready(), "Boot timeout"

    runner = vm_inst.ssh_run(["wget", "https://www.baidu.com/"], vm_ssh_key)
    assert runner.retcode == 0, "Failed to execute remote command"


def test_tdvm_ssh_forward(vm_factory, vm_ssh_pubkey, vm_ssh_key):
    """
    Test SSH forward functionality within TD guest
    """
    LOG.info("Create TD guest")
    inst = vm_factory.new_vm(VM_TYPE_TD)
    inst.image.inject_root_ssh_key(vm_ssh_pubkey)

    # create and start VM instance
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    runner = inst.ssh_run(["ls", "/"], vm_ssh_key)
    assert runner.retcode == 0, "Failed to execute remote command"


def test_tdvm_bridge_network_ip(vm_factory):
    """
    Test wget functionality within TD guest, the network could be NAT, bridget.
    """

    LOG.info("Create TD guest")
    vm_inst = vm_factory.new_vm(VM_TYPE_TD)

    # create and start VM instance
    vm_inst.create()
    vm_inst.start()
    assert vm_inst.wait_for_ssh_ready(), "Boot timeout"

    vm_bridge_ip = vm_inst.get_ip()
    assert vm_bridge_ip is not None

    runner = NativeCmdRunner(["ping", "-c", "3", vm_bridge_ip])
    runner.runwait()
    assert runner.retcode == 0
