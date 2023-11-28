#!/usr/bin/env python3

import sys
import subprocess
import os
import shutil

if len(sys.argv) < 2:
    print("Please provide the source file path as an argument.")
    sys.exit(1)


# Get the current working directory
streamflow_dir = os.getcwd()

source_file_path = os.path.abspath(sys.argv[1])
source_file_dir = os.path.dirname(source_file_path)
source_file_name = os.path.basename(source_file_path)
source_file_name_without_extension, source_file_extension = os.path.splitext(source_file_name)

kernel_transformer_dir = streamflow_dir + "/kernel_transformer"
clava_dir = kernel_transformer_dir + "/clava"
clava_unroll_path = kernel_transformer_dir + "/unroll.js"

unrolled_code_dir = source_file_dir + "/unrolled_code"
unrolled_code_path = unrolled_code_dir + "/" + source_file_name
clava_flatten_path = kernel_transformer_dir + "/flatten.js"

flatten_code_dir = source_file_dir + "/flatten_code"
flatten_code_path = flatten_code_dir + "/" + source_file_name
clava_morpher_format_path = kernel_transformer_dir + "/morpher_format.js"


# Unroll the code
command = ["java", "-jar", "Clava.jar", clava_unroll_path, "-p", source_file_path, "-o", source_file_dir, "-of", "unrolled_code"]

try:
    subprocess.run(command, check=True, cwd=clava_dir)
    print("Clava unroll transformation completed successfully.")
except subprocess.CalledProcessError as e:
    print("Clava unroll transformation failed:", e)

# Flatten the code
command = ["java", "-jar", "Clava.jar", clava_flatten_path, "-p", unrolled_code_path, "-o", source_file_dir, "-of", "flatten_code"]

try:
    subprocess.run(command, check=True, cwd=clava_dir)
    print("Clava flatten transformation completed successfully.")
except subprocess.CalledProcessError as e:
    print("Clava flatten transformation failed:", e)

# Format code for Morpher
command = ["java", "-jar", "Clava.jar", clava_morpher_format_path, "-p", flatten_code_path, "-o", source_file_dir, "-of", "morpher_formatted_code"]

try:
    subprocess.run(command, check=True, cwd=clava_dir)
    print("Clava morpher format transformation completed successfully.")
except subprocess.CalledProcessError as e:
    print("Clava morpher format transformation failed:", e)



# shutil.move(source_file_dir + "/woven_code/" + source_file_name, os.path.join(source_file_dir, source_file_name_without_extension + "_woven" + source_file_extension))
# shutil.rmtree(source_file_dir + "/woven_code/")