# Fixed on Alpine 3.16 for now until OpenSSL bug is fixed.
FROM alpine:3.16

# Install Required packages
RUN apk update
RUN apk add openconnect
RUN apk add python3
RUN apk add py3-pip
RUN apk add openssl
RUN apk add dante-server
RUN apk add tmux
RUN apk add bash
RUN apk add py3-requests

RUN python3 -m pip install bs4
# Clean up apk cache
RUN rm -rf /var/cache/apk/*

# Copy Socks config file to /etc
COPY sockd.conf /etc/
COPY entry.sh /
COPY vpn_auth.py /

# Open local port for proxy
EXPOSE 1080

# Fix permissions of entry.sh
RUN chmod 777 /entry.sh

ENTRYPOINT ["/entry.sh"]