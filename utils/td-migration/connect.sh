#!/bin/bash
set -e

modprobe vhost_vsock
socat TCP4-LISTEN:9009,reuseaddr VSOCK-LISTEN:1234,fork &
socat TCP4-CONNECT:127.0.0.1:9009,reuseaddr VSOCK-LISTEN:1235,fork &
