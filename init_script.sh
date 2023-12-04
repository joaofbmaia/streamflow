#!/bin/bash

# Dependencies
#sudo apt install graphviz


# Create the clava directory if it doesn't exist
mkdir -p kernel_transformer/clava

# Download the clava.zip file
wget http://specs.fe.up.pt/tools/clava.zip -O clava.zip

# Unzip the clava.zip file into the clava directory
unzip clava.zip -d kernel_transformer/clava

# Remove the clava.zip file
rm clava.zip

# Build LLVM
git clone https://github.com/llvm/llvm-project.git
cd llvm-project
git checkout llvmorg-10.0.0
# Replace benchmark_register.h file
wget https://github.com/llvm/llvm-project/raw/llvmorg-12.0.0/llvm/utils/benchmark/src/benchmark_register.h -O llvm/utils/benchmark/src/benchmark_register.h
mkdir llvm-build
cd llvm-build
cmake -DLLVM_ENABLE_PROJECTS='polly;clang' -DLLVM_USE_LINKER=gold -DLLVM_TARGETS_TO_BUILD="X86" -G "Unix Makefiles" ../llvm
make -j$(nproc)

cd ../..

# Build DFG Generator
cd dfg_generator
mkdir build
cd build
cmake ..
make VERBOSE=1 -j$(nproc)

cd ../..

# Build CGRA Mapper
cd cgra_mapper
mkdir build
cd build
cmake ..
make all -j$(nproc)