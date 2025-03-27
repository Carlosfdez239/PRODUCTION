#!/bin/bash


if [ ! -d "output" ]; then
    mkdir output
fi 

# Prompt the user for the LYRAP serial number to use as part of the output file name
read -p "Ingrese el número de serie de Datamatrix para el archivo de salida: " lectura

type="Vib"

# Redirect all output to the specified file
#output_path="output/${output_file}_${type}.txt"
output_path="output/${$lectura}_${type}.txt"
exec > >(tee "$output_path") 2>&1

make VIB

# remove ansi escape codes (that are used for formatting the output in the terminal)
sed -i -e 's/\r//g' -e 's/\x1B\[[0-9;]*[JKmsu]//g' "$output_path"

