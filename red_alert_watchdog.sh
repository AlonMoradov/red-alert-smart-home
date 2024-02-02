#!/bin/bash

SCRIPT_NAME="red_alert.sh"

# Check if the script is already running
PID=$(pgrep -f "$SCRIPT_NAME")

# If the script is not running, start it
if [[ -z "$PID" ]]; then
    bash "$SCRIPT_NAME"
else
    echo "The script '$SCRIPT_NAME' is already running."
fi
