# TDX Deployment Tool

Deploy TDX host or guest packages to managed nodes (TDX guest or host nodes) using an ansible control node.
The tool builds control node, handles the ansible setup and execution in docker.

## Build docker image

As a convenience, use the command to build the docker image defined by Dockerfile.

```
./docker-playbook.sh rebuild
```

## Build default inventory

Please configure below sections in default inventory file [`config-ansible/hosts`](config-ansible/hosts):

- Create a `hosts` file with all managed node information
- Setup ssh password-less login on each node which is prerequisite for ansible:
  - `ssh-copy-id <ansible_user>@<managed_node>`
  - Please get more details from Ansible official document at <https://docs.ansible.com/ansible/latest/user_guide/connection_details.html#setting-up-ssh-keys>

## Run deployment playbook

_NOTE： if the `repo_typ` is `build_repo`, please copy all pre-built packages into `<tdx-tools>/deploy/tdx_stack/tdx_repo/`._

1. Install packages to TDX host nodes

```
./docker-playbook.sh -i hosts tdx_stack/tdx_host_install.yml -K
```
