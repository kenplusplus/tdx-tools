"""
Basic host status checking for MKTME, TDX, SGX, SEAMRR etc.
"""

import logging
import os.path
import glob
from pycloudstack import msr, dut

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


def test_tdx_enabled_in_bios():
    """
    Check whether the bit 11 for MSR 0x1401, 1 means TDX is enabled in BIOS.

    Test Steps
    ----------
    1. Read the bit 11 of the value of MSR 0x1401
    2. Check whether bit 11 is 1
    3. If not 1, print the value of MSR 0xa0 for error code
    """
    msrobj = msr.MSR()
    tdx_val = msrobj.readmsr(0x1401, 11, 11)
    if tdx_val != 1:
        error_val = msrobj.readmsr(0xa0)
        LOG.error("Error (MSR 0xa0): %X", error_val)
    assert tdx_val == 1


def test_mktme_enabled_in_bios():
    """
    Check whether MK-TME is enabled in BIOS
    https://software.intel.com/sites/default/files/managed/a5/16/Multi-Key-Total-Memory-Encryption-Spec.pdf

    Test Steps
    ----------
    1. Read the bit 1 of the value of MSR 0x982
    2. Check whether bit 1 is 1
    3. If not 1, the MK-TME is not enabled
    """
    msrobj = msr.MSR()
    mktme_val = msrobj.readmsr(msr.MSR.IA32_TME_ACTIVATE)
    assert mktme_val & 0x2 != 0


def test_sgx_enabled_in_bios():
    """
    Check whether SGX is enabled in BIOS
    https://software.intel.com/sites/default/files/managed/48/88/329298-002.pdf

    Test Steps
    ----------
    1. Read the bit 18 of the value of MSR IA32_FEATURE_CONTROL
    2. Check whether bit 18 is 1
    3. If not 1, the SGX is not enabled
    """
    msrobj = msr.MSR()
    sgx_val = msrobj.readmsr(msr.MSR.IA32_FEATURE_CONTROL, 18, 18)
    assert sgx_val == 1


def test_sgx_supported_in_cpuinfo():
    """
    Check whether SGX is enabled in /proc/cpuinfo
    Even if SGX is supported by platform, user can disable sgx by adding 'nosgx' in kernel
    command line. If sgx appears in the /proc/cpuinfo, it means that sgx is enabled

    Test Steps
    ----------
    1. Read /proc/cpuinfo
    2. Check whether 'sgx' is in flags field
    """
    assert dut.DUT.support_sgx()


def test_check_mktme_keyid_bits():
    """
    check Keys bits of MK-TME
    https://software.intel.com/sites/default/files/managed/a5/16/Multi-Key-Total-Memory-Encryption-Spec.pdf
    """
    msrobj = msr.MSR()
    mktme_keyid_bits = msrobj.readmsr(msr.MSR.IA32_TME_ACTIVATE, 35, 32)
    mktme_max_keys = msrobj.readmsr(msr.MSR.IA32_TME_CAPABILITY, 50, 36)
    LOG.info("MK-TME max keys=%d, MK-TME key bits=%d",
        mktme_max_keys, mktme_keyid_bits)
    assert (2 ^ mktme_keyid_bits) < mktme_max_keys

def test_check_tdx_keyid_bits():
    """
    check Keys bits of TDX
    """
    msrobj = msr.MSR()
    tdx_keyid_bits = msrobj.readmsr(msr.MSR.IA32_TME_ACTIVATE, 39, 36)
    mktme_max_keys = msrobj.readmsr(msr.MSR.IA32_TME_CAPABILITY, 50, 36)
    LOG.info("MK-TME max keys=%d, TDX key bits=%d",
        mktme_max_keys, tdx_keyid_bits)
    assert (2 ^ tdx_keyid_bits) < mktme_max_keys

def test_check_tdx_key_numbers():
    """
    check Keys bits of TDX
    """
    msrobj = msr.MSR()
    tdx_key_num = msrobj.readmsr(msr.MSR.IA32_MKTME_PARTITIONING, 63, 32)
    LOG.info("TDX key number=%d", tdx_key_num)
    assert tdx_key_num > 0


def test_check_sgx_mcheck_error():
    """
    check whether SGX mcheck error is 0
    """
    msrobj = msr.MSR()
    sgx_mcheck_error = msrobj.readmsr(msr.MSR.SGX_MCU_ERRORCODE)
    LOG.info("SGX MCHECK error=%d", sgx_mcheck_error)
    assert sgx_mcheck_error == 0

def test_check_sgx_debug_status():
    """
    check whether SGX debug is enabled, it should be disabled for attestation
    validation.
    """
    msrobj = msr.MSR()
    sgx_debug_status = msrobj.readmsr(msr.MSR.SGX_DEBUG)
    LOG.info("SGX Debug =%d", sgx_debug_status)


def test_check_sgx_dev_node_exist():
    """
    check whether '/dev/sgx_provision' exists
    """
    assert os.path.exists('/dev/sgx_provision')


def test_check_sgx_registration_status():
    """
    check whether '/sys/firmware/efi/efivars/SgxRegistrationStatus-*' is exist
    """
    assert len(glob.glob('/sys/firmware/efi/efivars/SgxRegistrationStatus-*')) == 1
