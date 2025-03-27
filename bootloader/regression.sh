#!/bin/bash -
# By default the script leaves the TrustZone enabled after regression
TRUSTZONE_ENABLE="${1:-1}"
[[ "${TRUSTZONE_ENABLE}" =~ 0|1 ]] || exit 1

echo "regression script started"
stm32programmercli="$ST_PROGRAMMER_PATH/STM32_Programmer_CLI"
secbootadd0=0x1800c0
flashsectnbr=0xff
oem2_key_word0=0xd5cea9b1
oem2_key_word1=0x16e6b885
connect="-c port=SWD mode=UR --hardRst"
connect_no_reset="-c port=SWD mode=HotPlug"
rdp_0="-ob RDP=0xAA TZEN=${TRUSTZONE_ENABLE} UNLOCK_1A=1 UNLOCK_1B=1 UNLOCK_2A=1 UNLOCK_2B=1"
remove_bank1_protect="-ob SECWM1_PSTRT="$flashsectnbr" SECWM1_PEND=0 WRP1A_PSTRT="$flashsectnbr" WRP1A_PEND=0 WRP1B_PSTRT="$flashsectnbr" WRP1B_PEND=0"
remove_bank2_protect="-ob SECWM2_PSTRT="$flashsectnbr" SECWM2_PEND=0 WRP2A_PSTRT="$flashsectnbr" WRP2A_PEND=0 WRP2B_PSTRT="$flashsectnbr" WRP2B_PEND=0"
erase_all="-e all"
remove_hdp_protection="-ob HDP1_PEND=0 HDP1EN=0 HDP2_PEND=0 HDP2EN=0"
default_ob1="-ob SRAM2_RST=0 NSBOOTADD0=0x100000 NSBOOTADD1=0x17f200 BOOT_LOCK=0 SECBOOTADD0="$secbootadd0" DBANK=1 SWAP_BANK=0 nSWBOOT0=1 SECWM1_PSTRT=0 SECWM1_PEND="$flashsectnbr""
default_ob2="-ob SECWM2_PSTRT=0 SECWM2_PEND="$flashsectnbr""
oem_lock2="-lockRDP2 ${oem2_key_word0} ${oem2_key_word1}"

#$stm32programmercli $connect_no_reset -unlockRDP2 ${oem2_key_word0} ${oem2_key_word1} # --> 27/03/2025 usamos $connect para poder limpiar las placas mal grabadas
$stm32programmercli $connect -unlockRDP2 ${oem2_key_word0} ${oem2_key_word1}
# the previous command will "fail" (return code 1), but it should display "Unlock RDP2 password succefully done!" in the output.
read -p "RESET the device and then press a key" -n1 -s; 

echo "Retrieving Authentication ID" 
$stm32programmercli $connect_no_reset getAuthID
# the previous command will "fail"(return code 1), but the ID should have been read anyways.
echo "Regression to RDP 0, trustzone is left enabled/disabled depending on TRUSTZONE_ENABLE value"
$stm32programmercli $connect_no_reset $rdp_0
ret=$?
if [ $ret != 0 ]; then
  $stm32programmercli $connect $rdp_0
  ret=$?
  if [ $ret != 0 ]; then
    if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
    exit 1
  fi
fi

echo "Clear previous OEM2 key"
$stm32programmercli $connect -lockRDP2 0xFFFFFFFF 0xFFFFFFFF
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "Provision default OEM2 key"
$stm32programmercli $connect $oem_lock2
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "Remove bank1 protection"
$stm32programmercli $connect $remove_bank1_protect
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "Remove bank2 protection and erase all"
$stm32programmercli $connect_no_reset $remove_bank2_protect $erase_all
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "Remove hdp protection"
$stm32programmercli $connect_no_reset $remove_hdp_protection
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "Set default OB 1 (dual bank, swap bank, sram2 reset, secure entry point, bank 1 full secure)"
$stm32programmercli $connect_no_reset $default_ob1
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
echo "Set default OB 2 (bank 2 full secure)"
$stm32programmercli $connect_no_reset $default_ob2
ret=$?
if [ $ret != 0 ]; then
  if [ "$1" != "AUTO" ]; then read -p "regression script failed, press a key" -n1 -s; fi
  exit 1
fi
if [ "$1" != "AUTO" ]; then read -p "regression script Done, press a key" -n1 -s; fi
exit 0
