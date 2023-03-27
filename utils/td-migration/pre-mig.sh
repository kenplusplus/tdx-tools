#!/bin/bash
set -e

# Asking migtd-dst to connect to the src socat
echo "qom-set /objects/tdx0/ vsockport 1234" | nc -U /tmp/qmp-sock-src

# Asking migtd-dst to connect to the dst socat
echo "qom-set /objects/tdx0/ vsockport 1235" | nc -U /tmp/qmp-sock-dst
