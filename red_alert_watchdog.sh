#!/bin/bash

SCRIPT_NAME="red_alert.py"

# Check if the script is already running
PID=$(pgrep -f "$SCRIPT_NAME")

# If the script is not running, start it
if [[ -z "$PID" ]]; then
    nohup $HOME/red_alert_hue_lights/venv/bin/python3 $HOME/red_alert_hue_lights/$SCRIPT_NAME > $HOME/red_alert.log 2>&1 &
else
    echo "The script '$SCRIPT_NAME' is already running."
fi
