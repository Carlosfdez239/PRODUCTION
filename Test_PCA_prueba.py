import serial as ser


PUERTO= "/dev/ttyUSB0"

comandos = [
    'TEST_VIN',
    "echo -e '\nTEST_STM32_ID'"
]

def activar_serial():
    conexion = ser.Serial(PUERTO,115200,timeout=1)
    return conexion

def main():
    con = activar_serial()
    for comando in comandos:
        print(f'valor de comando --> {comando}')
        result = con.write(comando.encode())
        print(f'test enviado --> {result}')
        leido = con.read().decode()
        print(f'Valor recibido --> {leido}')
    con.close()

if __name__== "__main__":
    main()