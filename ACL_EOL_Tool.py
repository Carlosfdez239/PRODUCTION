'''
C. Fdez
29/01/2025

Tool que permite lanzar los comandos sobre nodos ACL G7
Los nodos deben tener instalado el PCA_Test.

Version
    29/01/2025 --> rev 1

TO DO:
    []
    []


'''

import subprocess
import os
import time
import serial

Puerto_DUT = ""
PCA_COMMANDS = {"TEST_VERSION":'\nTEST_VERSION\n',                  # 0
                "TEST_STM32_ID":'\nTEST_STM32_ID\n',                # 1
                "TEST_FLASH":'\nTEST_FLASH\n',                      # 2
                "TEST_FLASH_ENABLE":'\nTEST_FLASH_ENABLE\n',        # 3
                "TEST_FLASH_DISABLE":'\nTEST_FLASH_DISABLE\n',      # 4
                #"TEST_REBOOT":'\nTEST_REBOOT\n',                    # 5
                "TEST_VIN":'\nTEST_VIN\n',                          # 6
                "TEST_TEMP_HUM":'\nTEST_TEMP_HUM\n',                # 7
                #"TEST_LOWPOW":'\nTEST_LOWPOW\n',                    # 8
                #"TEST_FULL_POW":'\nTEST_FULL_POW\n',                # 9
                "TEST_LP_ACC":'\nTEST_LP_ACC\n',                    # 10
                "TEST_HP_ACC":'\nTEST_HP_ACC\n',                    # 11
                "TEST_MAG_MMC":'\nTEST_MAG_MMC\n',                  # 12
                "TEST_LORA_ENABLE":'\nTEST_LORA_ENABLE\n',          # 13
                "TEST_LORA_DISABLE":'\nTEST_LORA_DISABLE\n',        # 14
                #"TEST_LORA_TONE":'\nTEST_LORA_TONE\n',              # 15
                #"TEST_LORA_TX":'\nTEST_LORA_TX 868000 14 11\n',     # 16
                #"TEST_LORA_RX":'\nTEST_LORA_RX 868000 11 4000\n',   # 17
                "TEST_LORA_ID":'\nTEST_LORA_ID\n',                  # 18
                "TEST_BLE_ENABLE":'\nTEST_BLE_ENABLE\n',            # 19
                "TEST_BLE_DISABLE":'\nTEST_BLE_DISABLE\n',          # 20
                #"TEST_BLE_FW":'\nTEST_BLE_FW\n',                    # 21
                #"TEST_BLE_ID":'\nTEST_BLE_ID\n',                    # 22
                #"TEST_BLE_START_ADV":'\nTEST_BLE_START_ADV\n',      # 23
                #"TEST_BLE_STOP_ADV":'\nTEST_BLE_STOP_ADV\n',        # 24
                }
Informe = {
                "SERIAL":"",
                "TEST_VERSION":"",                  # 0
                "TEST_STM32_ID":"",                # 1
                "TEST_FLASH":"",                      # 2
                "TEST_FLASH_ENABLE":"",        # 3
                "TEST_FLASH_DISABLE":"",      # 4
                "TEST_REBOOT":"",                    # 5
                "TEST_VIN":"",                          # 6
                "TEST_TEMP_HUM":"",                # 7
                "TEST_LOWPOW":"",                    # 8
                "TEST_FULL_POW":"",                # 9
                "TEST_LP_ACC":"",                    # 10
                "TEST_HP_ACC":"",                    # 11
                "TEST_MAG_MMC":"",                  # 12
                "TEST_LORA_ENABLE":"",          # 13
                "TEST_LORA_DISABLE":"",        # 14
                "TEST_LORA_TONE":"",              # 15
                "TEST_LORA_TX":"",     # 16
                "TEST_LORA_RX":"",   # 17
                "TEST_LORA_ID":"",                  # 18
                "TEST_BLE_ENABLE":"",            # 19
                "TEST_BLE_DISABLE":"",          # 20
                "TEST_BLE_FW":"",                    # 21
                "TEST_BLE_ID":"",                    # 22
                "TEST_BLE_START_ADV":"",      # 23
                "TEST_BLE_STOP_ADV":""}        # 24


def Buscar_tty(serial):
    try:
        
        dispositivos = subprocess.run(['sudo','dmesg'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      text=True)
        
        salida = dispositivos.stdout.splitlines()
        #print(f'dispositivos encontrados: {salida}')

        for linea in salida:
            if serial in linea:
                #print (f'Contenido de la linea: {linea}')
                parts = linea.split(":")
                usb = parts[0]
                usb_buscado = usb[-8:]
                #print(f'usb buscado --> {usb_buscado}')
                for linea in salida:
                    if usb_buscado in linea:
                        #print (f'Datos del usb_buscado --> {linea}')
                        if "ttyUSB" in linea:
                            tty_original = linea.split(":")
                            disp_original= tty_original[1]
                            #print(f'dispositivo encontrado --> {disp_original}')
                            valor_tty_encontrado = disp_original[-7:]
                            #print(f'valor tty encontrado --> {valor_tty_encontrado}')
                ruta_completa_dispositivo = f'/dev/{valor_tty_encontrado}'
                #print(f'Ruta dispositivo encontrado --> {ruta_completa_dispositivo}')
                #print (f'Enlace simbolico creado: {enlace_simbolico} --> {ruta_original}')
                return ruta_completa_dispositivo
            #print(f'No se ha encontrado ningún dispositivo que coincida')
    except Exception as e:
        print(f'Error al ejecutar el scrip --> {e}')

def main(DUT):
    
    ser = serial.Serial(DUT, 115200,timeout=1)
    for clave, valor in PCA_COMMANDS.items():
        test = clave
        CMD = valor
        print(f'Test enviado --> {CMD}')
        ser.write(CMD.encode())
        #time.sleep(0.4)
        res = []
        while True:
            linea = ser.readline().decode().strip()
            print(f'Respuesta recibida --> {linea}')
            if linea:
                res.append(linea)
                Informe[clave]= res
            if linea == ">OK":
                #res.append(linea)
                break
        time.sleep(1)
    print(f'Respuesta recibida --> {res}')
    ser.close()
        
    Informe[clave] = res
    print(f'Contenido de Informe: {Informe}')
    #salida = Test.stdout.splitlines()

    return

if __name__ == "__main__":
    #Puerto_DUT = Buscar_tty('4eae75b7067ced11aae061f72f219a6d')
    #print(f'Dut encontrado en el puerto     --> {Puerto_DUT}')
    #Puerto_SAMPLE = Buscar_tty('16c299e9067ced11ad5462f72f219a6d')
    #print(f'Sample encontrado en el puerto  --> {Puerto_SAMPLE}')
    #Serial = input(f'Introduce el número de serie del equipo: ')
       
    main("/dev/ttyUSB0")
    #main(Puerto_DUT, Puerto_SAMPLE)