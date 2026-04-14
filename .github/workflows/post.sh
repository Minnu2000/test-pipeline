#!/bin/bash

# Create the releases directory
mkdir -p releases

# Move the binary generated in the previous step
if [ -f "./hello_executable" ]; then
    cp ./hello_executable ./releases/
fi

# Move any other generated artifacts/folders
if [ -d "./artifacts" ]; then
    cp -r ./artifacts ./releases/
fi

echo "Releases folder prepared."