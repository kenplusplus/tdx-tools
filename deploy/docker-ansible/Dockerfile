# SPDX-License-Identifier: MIT

FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install --no-install-recommends -y python3 python3-pip git ssh sudo && \
    rm -rf /var/lib/apt/lists/*

# Install the dependency files
COPY requirements_pip.txt docker-ansible-entry.sh /

# Install the dependencies of pip packages
RUN sudo -H python3 -m pip install --no-cache-dir -r /requirements_pip.txt

# Add worker user for security consideration
RUN useradd -d /home/tdxdev -m -s /bin/bash tdxdev && \
    adduser tdxdev sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER tdxdev

ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_RETRY_FILES_ENABLED false

VOLUME /home/tdxdev/deployment/
WORKDIR /home/tdxdev/deployment/

ENTRYPOINT ["/docker-ansible-entry.sh"]
