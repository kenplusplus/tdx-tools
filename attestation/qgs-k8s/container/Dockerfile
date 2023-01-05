FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG QGS_VERSION="1.15.100.3-jammy1"

RUN apt-get update && apt-get install -y wget gnupg

RUN wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | \
    gpg --dearmor --output /usr/share/keyrings/intel-sgx.gpg
RUN echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/intel-sgx.gpg] https://download.01.org/intel-sgx/sgx_repo/ubuntu jammy main' |\
    tee /etc/apt/sources.list.d/intel-sgx.list

RUN apt-get update && apt-get install -y tdx-qgs=${QGS_VERSION} && \
    rm -rf /var/lib/apt/lists/*

CMD ["/opt/intel/tdx-qgs/qgs", "--no-daemon"]
