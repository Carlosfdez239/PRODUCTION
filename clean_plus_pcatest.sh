#!/bin/bash

if [ ! -d "clean_output" ]; then
    mkdir clean_output
fi 

# Prompt the user for the LYRAP serial number to use as part of the output file name
read -p "Escanea la placa para continual " lectura

proceso="clean"
echo $proceso

# Redirect all output to the specified file
#output_path="output/${output_file}_${type}.txt"
#output_path="clean_output/111.txt"
output_path="clean_output/${lectura}_${proceso}.txt"
echo $output_path
exec > >(tee "$output_path") 2>&1

bash ~/Documents/G7/PRODUCTION/bootloader/regression.sh
bash ~/Documents/G7/PRODUCTION/bootloader.sh
bash ~/Documents/G7/PRODUCTION/flash_and_configure.sh TIL

# remove ansi escape codes (that are used for formatting the output in the terminal)
sed -i -e 's/\r//g' -e 's/\x1B\[[0-9;]*[JKmsu]//g' "$output_path"
