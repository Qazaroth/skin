#!/usr/bin/env bash

cd "$(dirname "$0")"

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt
    touch .deps_installed
fi

python3 main.py