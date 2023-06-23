# TDX Deployment Tool

Deploy TDX host environments to managed nodes using an ansible control node.  
The tool builds control node, handles the ansible setup and execution in docker. 

## Build docker image
As a convenience, use the command to build the docker image defined by Dockerfile.  
```
./docker-playbook.sh rebuild
```

## Build default inventory

Please configure below sections in default inventory file [`config-ansible/hosts`](config-ansible/hosts):

- Add managed nodes (hostname or ip address) to `[all]` section
- Configure user (`ansible_user`) for managed nodes in `[all:vars]`, otherwise will use default account (`tdxdev`) within docker
- Two approaches to deploy the TDX stack:
  - Approach 1: deploy the RPMs from local repository on the controller node
    - Copy/move the local repository directory named as `tdx-repository` to `<deployment tools>/tdx-sw-stack/tdx-repository`
    - Disable remote approach by commenting out [`tdx_remote_repo`](config-ansible/hosts)
  - Approach 2: deploy the RPMs from remote TDX repository such as `http://<my server url>/tdx-repository`
    - Configure remote URL `http://<my server url>/tdx-repository` in section [`tdx_remote_repo`](config-ansible/hosts)
- Setup ssh password-less login on each node which is prerequisite for ansible:
  - `ssh-copy-id <ansible_user>@<managed_node>`
  - Please get more details from Ansible official document at <https://docs.ansible.com/ansible/latest/user_guide/connection_details.html#setting-up-ssh-keys>

## Run deployment playbook
```
./docker-playbook.sh tdx-sw-stack/centos-td-host.yml
```
