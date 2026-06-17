#!/bin/bash

# post.sh - Save the config name to a file
# Usage: ./post.sh <config_name>

CONFIG_NAME=$1

echo "Config: $CONFIG_NAME" > build_config.txt
echo "Build completed at: $(date)" >> build_config.txt

echo "Saved config '$CONFIG_NAME' to build_config.txt"
cat build_config.txt