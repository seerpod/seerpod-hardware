#!/bin/bash

echo "Starting clearLog script....\n"
/usr/bin/truncate -s0 /opt/seerpod/logs/seerpod.log
echo "Logs truncated successfully."
echo "Stopping clearLog script."
