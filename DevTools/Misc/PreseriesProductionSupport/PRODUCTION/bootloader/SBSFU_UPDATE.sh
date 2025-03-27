#!/bin/bash -
echo "SBSFU_UPDATE started"
# Absolute path to this script
SCRIPT=$(readlink -f $0)
# Absolute path this script
SCRIPTPATH=`dirname $SCRIPT`
stm32programmercli="$ST_PROGRAMMER_PATH/STM32_Programmer_CLI"
connect_no_reset="-c port=SWD mode=UR"
connect="-c port=SWD mode=UR --hardRst"
# Information about how the address of boardstr is calculated:
# - boot_hal.c
#   static const char *board_string_addr = (const char *) ((BL2_NOHDP_CODE_START + BL2_NOHDP_CODE_SIZE) - BL2_BOARD_STR_LEN);
# - stm32u5xx_bl2.ld
#   FLASH_NOHDP (rx) : ORIGIN = ((((0x0C000000)) + ((((((0x0000) + ((0x2000))) + ((0x2000)) + (0x0000))+(0x2000))+(0x12000))))), LENGTH = ((((0x2000))) - (48))
#   ORIGIN + LENGTH - 0x30 (48 en hex)
#   ((((0x0C000000)) + ((((((0x0000) + ((0x2000))) + ((0x2000)) + (0x0000))+(0x2000))+(0x12000))))) + ((((0x2000))) - (0x30))
# The boardstr will be written in the PCA test
boardstr=0xc019fd0
slot0=0xc026000
slot1=0xc056000
slot2=0xc17e000
slot3=0xc1ae000
slot4=0x0
slot5=0x0
slot6=0x0
slot7=0x0
boot=0xc004000
loader=0xc3d2000
cfg_loader=1
app_image_number=2
s_data_image_number=0
ns_data_image_number=0

if [ $app_image_number == 2 ]; then
echo "Write SBSFU_Appli Secure"
$stm32programmercli $connect -d ./s_app_init.bin $slot0 -v
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "SBSFU_UPDATE script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "SBSFU_Appli Secure Written"
#echo "Write SBSFU_Appli NonSecure"
#$stm32programmercli $connect -d ./ns_app_sign.bin $slot1 -v
#ret=$?
#if [ $ret != 0 ]; then
#  if [ "$1" != "AUTO" ]; then read -p "SBSFU_UPDATE script failed, press a key" -n1 -s; fi
#  exit 1
#fi
#echo "SBSFU_Appli NonSecure Written"
fi

# write loader if config loader is active
if [ $cfg_loader == 1 ]; then
$stm32programmercli $connect -d ./loader.bin $loader -v
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "SBSFU_UPDATE script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "SBSFU_Loader Written"
fi
echo "Write SBSFU_SBSFU_Boot"
$stm32programmercli $connect -d ./sbsfu_boot.bin $boot -v
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "SBSFU_UPDATE script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "SBSFU_SBSFU_Boot Written"
$stm32programmercli $connect -d boardstr.bin $boardstr -v --skipErase
if [ "$1" != "AUTO" ]; then read -p "SBSFU_UPDATE script Done, press a key" -n1 -s; fi
exit 0
