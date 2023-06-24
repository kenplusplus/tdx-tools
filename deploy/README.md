# TDX Deployment Tool

Deploy TDX host or guest packages to managed nodes (TDX guest or host nodes) using an ansible control node.
The tool builds control node, handles the ansible setup and execution in docker.

Use the host deployment as example, see below picture:
![](/doc/tdx_host_deployment_ansible.png)

## Build docker image

As a convenience, use the command to build the docker image defined by Dockerfile.

```
./docker-playbook.sh rebuild
```

## Build default inventory

Please configure below sections in default inventory file [`config-ansible/hosts`](config-ansible/hosts):

- Create a `hosts` inventory file, please refer [How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- Setup ssh password-less login on each node which is prerequisite for ansible, simple steps are:
  - Use `ssh-keygen` to generate your key on controller node.
  - Use `ssh-copy-id <ansible_user>@<managed_node>` to enable passwordless login.
  - Please get more details from Ansible official document at <https://docs.ansible.com/ansible/latest/user_guide/connection_details.html#setting-up-ssh-keys>

## Run deployment playbook

_NOTE： if the `repo_typ` is `build_repo`, please copy all pre-built packages into `<tdx-tools>/deploy/tdx_stack/tdx_repo/`._

1. Install packages to TDX host nodes

```
./docker-playbook.sh -i hosts tdx_stack/tdx_host_install.yml -K
```
