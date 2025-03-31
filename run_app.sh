#!/bin/bash

cd "$(dirname "$0")/playground" || { echo "Error: Folder 'playground' does not exist"; exit 1; }

python3 user_interface.py
