#!/bin/bash

# Create the clava directory if it doesn't exist
mkdir -p kernel_transformer/clava

# Download the clava.zip file
wget http://specs.fe.up.pt/tools/clava.zip -O clava.zip

# Unzip the clava.zip file into the clava directory
unzip clava.zip -d kernel_transformer/clava

# Remove the clava.zip file
rm clava.zip

# Build DFG Generator
cd dfg_generator
mkdir build
cd build
cmake ..
make VERBOSE=1 -j 4