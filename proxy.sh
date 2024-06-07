#! /bin/bash
docker run --rm -it --privileged --cap-add SYS_ADMIN -h openconnect-socks --name openconnect-socks -p 127.0.0.1:1080:1080 --env-file openconnect-socks.env jpitcairn/openconnect-socks:2.0