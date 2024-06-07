#!/usr/bin/env sh

# Start Tmux server
tmux start-server

# create a session with VPN and SOCKS windows
tmux new-session -d -s OCSOCK -n SOCKS -d 'while ! ip link show tun0 | grep -q "UP"; do sleep 2; done; sockd'
tmux new-window -t OCSOCK:1 -n VPN "bash -c 'python3 /vpn_auth.py'"

# Attack to tmux session
tmux attach -t OCSOCK