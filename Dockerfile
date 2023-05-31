# Fixed on Alpine 3.16 for now until OpenSSL bug is fixed.
FROM alpine:3.16

# Install Required packages
RUN apk update
RUN apk add openconnect
RUN apk add openssl
RUN apk add dante-server
RUN apk add tmux

# Clean up apk cache
RUN rm -rf /var/cache/apk/*

# Copy Socks config file to /etc
COPY sockd.conf /etc/
COPY entry.sh /

# Open local port for proxy
EXPOSE 1080

# Fix permissions of entry.sh
RUN chmod 777 /entry.sh

ENTRYPOINT ["/entry.sh"]