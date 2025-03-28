import matplotlib.pyplot as plt
import pandas as pd

# The file is generated by executing:
# $ make showlog | ts '[%Y-%m-%d %H:%M:%S]' | ansi2txt | tee logfile_$(date '+%Y-%m-%d_%H-%M-%S').txt
log_file = "Firmware/LoadSensingG_App/armgcc/logfile_2023-05-05_10-51-30.txt"


with open(log_file) as f:
    lines = [line.rstrip() for line in f]
    # lines = [line for line in f]
# print(lines)


############################
# [2023-05-04 17:25:51] Raw data 999: -26, 64, 625']
# raw_data_lines = [line for line in lines if "Raw data" in line]
# print(raw_data_lines)
#
# columns = ["date", "x", "y", "z"]
#
# rms = []
# for line in raw_data_lines:
#    date_str = line.split('[')[1].split(']')[0]
#    raw_x = float(line.split(' ')[5].split(',')[0])/1e6
#    raw_y = float(line.split(' ')[6].split(',')[0])/1e6
#    raw_z = float(line.split(' ')[7])/1e6
#    rms.append([date_str, raw_x, raw_y, raw_z])
#    #print(type(line))
#
# print(rms)
# df = pd.DataFrame(rms, columns = columns)
# df['date'] = pd.to_datetime(df['date'])
## df = df.set_index('date')
# print(df)
#
# df[["x","y","z"]].plot()
# plt.show()


#############################
# [2023-05-05 10:51:38] MWRMS: 903781, 228488, 4404856
rms_lines = [line for line in lines if "MWRMS" in line]
# print(rms_lines)

columns = ["date", "rms_x", "rms_y", "rms_z"]
rms = []
for line in rms_lines:
    date_str = line.split("[")[1].split("]")[0]
    raw_x = float(line.split(" ")[3].split(",")[0]) / 1e6
    raw_y = float(line.split(" ")[4].split(",")[0]) / 1e6
    raw_z = float(line.split(" ")[5]) / 1e6
    rms.append([date_str, raw_x, raw_y, raw_z])
    # print(type(line))

# print(rms)
df = pd.DataFrame(rms, columns=columns)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")
# print(df)

df.plot()
plt.show()
