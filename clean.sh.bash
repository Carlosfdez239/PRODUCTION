#!/bin/bash

if [ ! -d "clean_output" ]; then
    mkdir clean_output
fi 

# Prompt the user for the LYRAP serial number to use as part of the output file name
read -p "Escanea la placa para continual " lectura

tipo = "clean"

# Redirect all output to the specified file
#output_path="output/${output_file}_${type}.txt"
output_path="clean_output/${$lectura}_{$tipo}.txt"
exec > >(tee "$output_path") 2>&1

./regression.sh

# remove ansi escape codes (that are used for formatting the output in the terminal)
sed -i -e 's/\r//g' -e 's/\x1B\[[0-9;]*[JKmsu]//g' "$output_path"
