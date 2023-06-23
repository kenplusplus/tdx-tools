# Ansible Role to Install TDX  Stack

# Variable

- repo_type: can be `remote_repo` or `build_repo`
  - `build_repo`: Copy the TDX packages at <tdx-tools>/deploy/tdx_task/tdx_repo/ to remote path `/srv/tdx_repo` for install
  - `remote_repo`: The TDX packages were already deployed on remote package repository server, just need add a repo (dnf/apt) to install.

# How to use

```
- name: "Setup TDX Repo"
  hosts: all
  become: true
  vars:
    repo_type: build_repo
    server_type: host
  roles:
    - setup_tdx_repo
```
