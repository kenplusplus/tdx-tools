#!/bin/bash

# SPDX-License-Identifier: MIT

if [[ ! -d ~/host_ssh/ ]]; then
    echo "Fail to find the host_ssh directory, please map via '-v' via docker run"
    exit 1
fi

# Copy the mapped host_ssh directory to tdxdev user's .ssh
sudo cp ~/host_ssh ~/.ssh -fr
sudo chown tdxdev:tdxdev ~/.ssh -R

# Correct the permission for the compabiltiy issue of different distros
chmod 700  ~/.ssh -R
chmod 600  ~/.ssh/id_rsa
chmod 644  ~/.ssh/id_rsa.pub

ansible-playbook "$@"
