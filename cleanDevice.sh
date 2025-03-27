#! /bin/bash
usbPath=$1

# 1. Unlock RDP
./STM32_Programmer_CLI -c port=SWD freq=1000 mode=UR -lockRDP2 0xD5CEA9B1 0x16E6B885

# 2. Disable TrustZone and set RDP 0
./STM32_Programmer_CLI -c port=SWD freq=1000 mode=HotPlug -ob RDP=0xAA TZEN=0

# 3. Reboot Device
echo -e "\nTEST_REBOOT\n" > $usbPath

# 4. Clear previous OEM1 key
./STM32_Programmer_CLI -c port=SWD freq=1000 mode=UR -lockRDP1 0xD5CEA9B1 0x16E6B885

# 5. Set the option byte RDP level to 1
./STM32_Programmer_CLI -c port=swd mode=hotplug -ob rdp=0xDC

# 6. Regress from RDP level 1 to RDP level 0 in order to unlock all the Writing Protections
./STM32_Programmer_CLI -c port=SWD mode=HotPlug -ob RDP=0xAA UNLOCK_1A=1 UNLOCK_1B=1 UNLOCK_2A=1 UNLOCK_2B=1

# 7. Crear previous OEM2 key
./STM32_Programmer_CLI -c port=SWD freq=1000 mode=UR -lockRDP2 0xFFFFFFFF 0xFFFFFFFF

# 8. Provision default OEM2 key
./STM32_Programmer_CLI -c port=SWD freq=1000 mode=UR -lockRDP2 0xD5CEA9B1 0x16E6B885

# 9. Remove bank1 protection
./STM32_Programmer_CLI -c port=SWD mode=UR -ob SECWM1_PSTRT=0xff SECWM1_PEND=0 WRP1A_PSTRT=0xff WRP1A_PEND=0 WRP1B_PSTRT=0xff WRP1B_PEND=0

# 10. Remove bank2 protection
./STM32_Programmer_CLI -c port=SWD mode=UR -ob SECWM2_PSTRT=0xff SECWM2_PEND=0 WRP2A_PSTRT=0xff WRP2A_PEND=0 WRP2B_PSTRT=0xff WRP2B_PEND=0

# 11. Remove HDP protection and erase all
./STM32_Programmer_CLI -c port=SWD mode=UR -ob HDP1_PEND=0 HDP1EN=0 HDP2_PEND=0 HDP2EN=0 -e all
