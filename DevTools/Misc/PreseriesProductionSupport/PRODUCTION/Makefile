.PHONY: regression bootloader vib

device ?= "LSG7ACL-BILH-VIB"

all:
	sudo apt-get install xdotool
	chmod +x ./bootloader/regression.sh
	chmod +x ./bootloader.sh
	chmod +x ./flash_and_configure.sh
	chmod +x ./lib/configure_device.sh
	chmod +x ./VIBR.sh
	chmod +x ./TIL90.sh

regression:
	export ST_PROGRAMMER_PATH=/opt/st_tools/CubeProgrammer/bin && ./bootloader/regression.sh

bootloader:
	export ST_PROGRAMMER_PATH=/opt/st_tools/CubeProgrammer/bin && ./bootloader.sh

VIB: 
	./flash_and_configure.sh VIB

TIL90:
	./flash_and_configure.sh TIL

