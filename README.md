# openconnect-socks
Tiny Docker container to proxy openconnect VPN traffic

## Install

1. Switch to directory containing Dockerfile.
2. Edit openconnect-socks.env to specify your username
3. Run `./build.sh`

## Usage

1. Run `./proxy.sh` and enter VPN credentials
2. Proxy will now be open on port 1080 on the docker host

