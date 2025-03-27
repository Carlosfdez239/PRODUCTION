#!/bin/bash

if [ ! -d "output" ]; then
    mkdir output
fi 

# Prompt the user for the LYRAP serial number to use as part of the output file name
read -p "Ingrese el número de serie de LYRAP para el archivo de salida: " output_file

type="bootloader"

# Redirect all output to the specified file
output_path="output/${output_file}_${type}.txt"
exec > >(tee "$output_path") 2>&1

# Function to run regression with expect
function run_regression {
  expect -c "
    spawn ./regression.sh
    set done_flag 0
    while {1} {
      expect {
        \"RESET the device and then press a key\" {
          send \n
        }
        \"regression script Done, press a key\" {
          if {\$done_flag == 0} {
            send \n
            set done_flag 1
          } else {
            break
          }
        }
        eof {
          break
        }
      }
    }
  "
}

# Function to display colored text
function echo_colored {
  local color="$1"
  local message="$2"
  local reset_color='\033[0m' # No Color
  echo -e "${color}${message}${reset_color}"
}

# Color codes
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Main script
echo_colored "$BLUE" "Vamos a cargar el bootloader en el Nodo."
echo_colored "$YELLOW" "Paso 1. Verificar si ambos cables USB están conectados al Nodo."

# Prompt the user to press a key to continue
read -n 1 -s -r -p "Presione cualquier tecla para continuar..."

export ST_PROGRAMMER_PATH="/opt/st_tools/CubeProgrammer/bin"

echo_colored "$YELLOW" "\nPaso 2. Ejecutando la regresión para preparar el Nodo."
cd bootloader
run_regression

# Wait 2 seconds
sleep 2

echo_colored "$YELLOW" "\nPaso 3. Descargando el bootloader en el Nodo."

expect -c "
  set timeout 20
  spawn ./SBSFU_UPDATE.sh
  expect \"SBSFU_UPDATE script Done, press a key\"
  send \n
  expect eof
"

cd ..
# Print "Bootloader flashed successfully" in green
echo_colored "$GREEN" "\nEl bootloader se ha flasheado correctamente."

read -n 1 -s -r -p "Presione una tecla para terminar..."

# remove ansi escape codes (that are used for formatting the output in the terminal)
sed -i -e 's/\r//g' -e 's/\x1B\[[0-9;]*[JKmsu]//g' "$output_path"
