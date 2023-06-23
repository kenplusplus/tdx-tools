# Ansbile Role for TDX Repo

# Tasks

- Copy RPMs to remote (local repository)
- Create repo for RPMs (local repository)
- Configure tdx repo

# Variable

- rpms_dir: local RPMs directory in control node
- remote_dir: remote path in managed node to store rpms_dir

# How to use
```
- name: Setup TDX Repo
  hosts: all
  become: true
  vars:
    repo_name: tdx-host-basic
    rpms_dir: tdx-repository
    remote_dir: /srv/
  roles:
    - setup_tdx_repo

```
