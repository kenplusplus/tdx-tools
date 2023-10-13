#!/bin/bash
# shellcheck disable=all
#export env var
while read env_var; do
  export "$env_var"
done < /etc/environment

# pull docker image
docker pull docker.io/library/nginx:latest
docker pull docker.io/library/redis:latest
docker pull docker.io/intel/intel-optimized-tensorflow-avx512:2.8.0
