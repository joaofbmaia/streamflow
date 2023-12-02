#!/usr/bin/env python3

import sys
import subprocess
import os
import shutil
import subprocess
import shutil

unrolled_code_dir_name = "0_unrolled_code"
flattened_code_dir_name = "1_flattened_code"
morpher_formatted_code_dir_name = "2_morpher_formatted_code"
dfg_gen_output_dir_name = "3_dfg_gen_output"

if len(sys.argv) < 3:
    print("Please provide the source file path as an argument.")
    sys.exit(1)

arg_csource = sys.argv[1]
function_name = sys.argv[2]

# Get the current working directory
streamflow_dir = os.getcwd()

source_file_path = os.path.abspath(arg_csource)
source_file_dir = os.path.dirname(source_file_path)
source_file_name = os.path.basename(source_file_path)
source_file_name_without_extension, source_file_extension = os.path.splitext(source_file_name)

kernel_transformer_dir = streamflow_dir + "/kernel_transformer"
clava_dir = kernel_transformer_dir + "/clava"
clava_unroll_path = kernel_transformer_dir + "/unroll.js"

unrolled_code_dir = source_file_dir + "/" + unrolled_code_dir_name
unrolled_code_path = unrolled_code_dir + "/" + source_file_name
clava_flatten_path = kernel_transformer_dir + "/flatten.js"

flatten_code_dir = source_file_dir + "/" + flattened_code_dir_name
flatten_code_path = flatten_code_dir + "/" + source_file_name
clava_morpher_format_path = kernel_transformer_dir + "/morpher_format.js"

morpher_formatted_code_dir = source_file_dir + "/" + morpher_formatted_code_dir_name
morpher_formatted_code_path = morpher_formatted_code_dir + "/" + source_file_name

dfg_gen_output_dir = source_file_dir + "/" + dfg_gen_output_dir_name
ll_ir_path = dfg_gen_output_dir + "/" + source_file_name_without_extension + ".ll"
ll_ir_opt_path = dfg_gen_output_dir + "/" + source_file_name_without_extension + "_opt.ll"
ll_ir_opt_instrument_path = dfg_gen_output_dir + "/" + source_file_name_without_extension + "_opt_instrument.ll"


#################### Kernel Transforms ####################

# Unroll the code
command = ["java", "-jar", "Clava.jar", clava_unroll_path, "-p", source_file_path, "-o", source_file_dir, "-of", unrolled_code_dir_name]

try:
    subprocess.run(command, check=True, cwd=clava_dir)
    print("Clava unroll transformation completed successfully.")
except subprocess.CalledProcessError as e:
    print("Clava unroll transformation failed:", e)

# Flatten the code
command = ["java", "-jar", "Clava.jar", clava_flatten_path, "-p", unrolled_code_path, "-o", source_file_dir, "-of", flattened_code_dir_name]

try:
    subprocess.run(command, check=True, cwd=clava_dir)
    print("Clava flatten transformation completed successfully.")
except subprocess.CalledProcessError as e:
    print("Clava flatten transformation failed:", e)

# Format code for Morpher
command = ["java", "-jar", "Clava.jar", clava_morpher_format_path, "-p", flatten_code_path, "-o", source_file_dir, "-of", morpher_formatted_code_dir_name]

try:
    subprocess.run(command, check=True, cwd=clava_dir)
    print("Clava morpher format transformation completed successfully.")
except subprocess.CalledProcessError as e:
    print("Clava morpher format transformation failed:", e)


#################### Morpher DFG Generator ####################

llvm_bin_dir = streamflow_dir + "/llvm-project/llvm-build/bin"
clang_bin = llvm_bin_dir + "/clang"
opt_bin = llvm_bin_dir + "/opt"
dfg_gen_dir = streamflow_dir + "/dfg_generator"
libdfggenPass_bin = dfg_gen_dir + "/build/src/libdfggenPass.so"

# Check if the directory exists
if os.path.exists(dfg_gen_output_dir):
    # Remove the directory
    shutil.rmtree(dfg_gen_output_dir)

# Create dfg_gen_output directory if it doesn't exist
os.makedirs(dfg_gen_output_dir, exist_ok=True)

# Run Clang
clang_command = [
    clang_bin,
    "-D",
    "CGRA_COMPILER",
    "-target",
    "i386-unknown-linux-gnu",
    "-Wno-implicit-function-declaration",
    "-Wno-format",
    "-Wno-main-return-type",
    "-fno-discard-value-names",
    "-c",
    "-emit-llvm",
    "-O2",
    "-fno-tree-vectorize",
    "-fno-slp-vectorize",
    "-fno-vectorize",
    "-fno-unroll-loops",
    morpher_formatted_code_path,
    "-S",
    "-o",
    ll_ir_path
]

try:
    subprocess.run(clang_command, check=True)
    print("Clang compilation executed successfully.")
except subprocess.CalledProcessError as e:
    print("Clang compilation failed:", e)

# Run opt pass
opt_command = [
    opt_bin,
    "-instnamer",
    "-gvn",
    "-mem2reg",
    "-memdep",
    "-memcpyopt",
    "-lcssa",
    "-loop-simplify",
    "-licm",
    "-loop-deletion",
    "-indvars",
    "-simplifycfg",
    "-mergereturn",
    "-indvars",
    ll_ir_path,
    "-S",
    "-o",
    ll_ir_opt_path
]

try:
    subprocess.run(opt_command, check=True)
    print("Optimizer executed successfully.")
except subprocess.CalledProcessError as e:
    print("Optimizer failed:", e)

numberofbanks = "2"
banksize = "2048"

# Generate DFG
dfg_gen_command = [
    opt_bin,
    "-load",
    libdfggenPass_bin,
    "-fn",
    function_name,
    "-nobanks",
    numberofbanks,
    "-banksize",
    banksize,
    "-type",
    "PartPred",
    "-skeleton",
    ll_ir_opt_path,
    "-S",
    "-o",
    ll_ir_opt_instrument_path
]

try:
    subprocess.run(dfg_gen_command, check=True, cwd=dfg_gen_output_dir)
    print("DFG generation successfully.")
except subprocess.CalledProcessError as e:
    print("DFG generation failed:", e)

dfg_dot_path = dfg_gen_output_dir + "/" + function_name + "_PartPredDFG.dot"
dfg_pdf_path = dfg_gen_output_dir + "/" + function_name + "_PartPredDFG.pdf"

simple_dfg_dot_path = dfg_gen_output_dir + "/" + function_name + "_PartPredDFG_simple.dot"
simple_dfg_pdf_path = dfg_gen_output_dir + "/" + function_name + "_PartPredDFG_simple.pdf"

# Generate PDF from DFG dot file
dot_command = ["dot", "-Tpdf", dfg_dot_path, "-o", dfg_pdf_path]

try:
    subprocess.run(dot_command, check=True)
    print("DFG PDF generated successfully.")
except subprocess.CalledProcessError as e:
    print("DFG PDF generation failed:", e)

# Generate PDF from simple DFG dot file
dot_command = ["dot", "-Tpdf", simple_dfg_dot_path, "-o", simple_dfg_pdf_path]

try:
    subprocess.run(dot_command, check=True)
    print("Simple DFG PDF generated successfully.")
except subprocess.CalledProcessError as e:
    print("Simple DFG PDF generation failed:", e)



