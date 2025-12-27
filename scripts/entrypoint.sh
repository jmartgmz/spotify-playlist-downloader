#!/bin/bash
set -e

# If a command is passed, run it
if [ $# -gt 0 ]; then
    exec "$@"
else
    # Otherwise, keep container alive and run launcher
    exec python launcher.py
fi
