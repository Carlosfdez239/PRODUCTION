import json
import os.path


class GenericModbusDataCfgs(object):
    GENERIC_MODBUS_MAX_DATA_SIZE = 312  # Maximum size of data in bits allowed at one frame

    def __init__(self, cfg_id):
        self.cfg_id = cfg_id
        self.is_valid_cfg = False
        self.csv_filename = ""
        self.manufacturer = ""
        self.sensor_model = ""
        self.description = ""
        self.channels_info = {}
        data_cfg_list = []

        dirname = os.path.dirname(__file__)
        self.cfg_filename = os.path.join(
            dirname, "./GenericModbusDataCfgs/generic_modbus_configs.json"
        )

        if os.path.isfile(self.cfg_filename):
            with open(self.cfg_filename, "r") as data_cfg_file:
                try:
                    data_cfg_list = json.load(data_cfg_file)
                except:
                    print("Error: File not detected as json file")

            if len(data_cfg_list) > 0:
                try:
                    for config in data_cfg_list:
                        if int(config["cfg_id"]) == int(self.cfg_id):
                            self.manufacturer = config["manufacturer"]
                            self.sensor_model = config["sensor_model"]
                            self.description = config["description"]
                            self.csv_filename = config["csv_filename"]
                            self.channels_info = config["channels"]
                            self.is_valid_cfg = True
                            break
                except:
                    print("Error: Configuration format not valid")
        else:
            print("Error: Configuration with id %u was not found") % self.cfg_id

    def get_sensors_per_frame(self):
        total_data = 0

        total_data += 1  # Response bit
        for chn in self.channels_info:
            total_data += chn["data_size"]

        return self.GENERIC_MODBUS_MAX_DATA_SIZE / total_data
