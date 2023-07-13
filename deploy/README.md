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

- Create a `hosts` inventory file, please refer [How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- Setup ssh password-less login on each node which is prerequisite for ansible, simple steps are:
  - Use `ssh-keygen` to generate your key on controller node.
  - Use `ssh-copy-id <ansible_user>@<managed_node>` to enable passwordless login.
  - Please get more details from Ansible official document at <https://docs.ansible.com/ansible/latest/user_guide/connection_details.html#setting-up-ssh-keys>

## Run deployment playbook


1. Install packages to TDX host nodes from build repository

![](/doc/tdx_deploy_ansible_from_build_repo.png)

_NOTE： if the `repo_type` is `build_repo`, please copy all pre-built packages into `<tdx-tools>/deploy/tdx_stack/tdx_repo/`._

```
./docker-playbook.sh -i hosts tdx_stack/tdx_host_install.yml -K
```

if want to reboot system after installation:
```
./docker-playbook.sh -i hosts tdx_stack/tdx_host_install.yml -e reboot_after_complete=true -K
```

2. Install packages from existing remote repositories

![](/doc/tdx_deploy_ansible_from_remote_repo.png)

_NOTE: please replace repositories list for `remote_repo_urls` in below._

```
./docker-playbook.sh -i hosts tdx_stack/tdx_host_install.yml -e repo_type=remote_repo -e '{"remote_repo_urls": ["deb [trusted=yes] http://css-devops.sh.intel.com/download/mvp-stacks/1.0/2023ww22/mvp-tdx-stack-host-ubuntu-22.04/jammy/amd64/ ./", "deb [trusted=yes] http://css-devops.sh.intel.com/download/mvp-stacks/1.0/2023ww22/mvp-tdx-stack-host-ubuntu-22.04/jammy/all/ ./"] }' -K
```
