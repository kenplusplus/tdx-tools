#!/bin/bash

# provide a repo containing packages grub2-efi-x64 and shim-x64
cat <<EOT >> /etc/yum.repos.d/GA.repo
[RHEL-9.2.0-GA-BaseOS]
name = RHEL-9.2.0-GA-BaseOS 
baseurl = [] 
enabled = 1
gpgcheck = 0
sslverify=0
EOT

dnf check-update

echo "update repos"

