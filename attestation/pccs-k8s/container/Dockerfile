FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PCCS_VERSION="1.15.100.3-jammy1"
ARG NPM_MIRROR="--registry=http://registry.npm.taobao.org"

RUN apt-get update && apt-get install -y wget gnupg

RUN wget https://download.01.org/intel-sgx/sgx-dcap/1.15/linux/distro/ubuntu22.04-server/sgx_debian_local_repo.tgz

RUN tar zxvf sgx_debian_local_repo.tgz && \
    rm -f sgx_debian_local_repo.tgz

RUN echo "deb [trusted=yes arch=amd64] file:/sgx_debian_local_repo jammy main" |\
    tee /etc/apt/sources.list.d/sgx_debian_local_repo.list

RUN wget -qO - https://deb.nodesource.com/setup_16.x | bash -

# The postinst will check the directory for configuration
RUN mkdir /etc/init/

RUN apt-get update && apt-get install -y --no-install-recommends nodejs sgx-dcap-pccs=${PCCS_VERSION} && \
    rm -rf /var/lib/apt/lists/*

RUN cd /opt/intel/sgx-dcap-pccs/ && \
    npm config set engine-strict true && \
    npm install ${NPM_MIRROR}

VOLUME /opt/intel/sgx-dcap-pccs/ssl_key/
VOLUME /data
WORKDIR /opt/intel/sgx-dcap-pccs/

EXPOSE 8081

CMD ["node", "pccs_server.js"]