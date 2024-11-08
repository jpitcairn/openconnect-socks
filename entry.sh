#!/usr/bin/env sh

# Start Tmux server
tmux start-server

# create a session with VPN and SOCKS windows
tmux new-session -d -s OCSOCK -n SOCKS -d 'while ! ip link show tun0 | grep -q "UP"; do sleep 2; done; sockd'
tmux new-window -t OCSOCK:1 -n VPN "openconnect $VPN_URL --user=$VPN_USER"

# Attack to tmux session
tmux attach -t OCSOCK