Dynamic Node Injector Tool
==========================

Injects accelerometer raw data to the DYN node via a serial link.

The node must be compiled to use the UART test accelerometer located in `Firmware/Libs/lib_test_accel/test_accel.c`.

## Compilation

There are two ways the DynInjector can be used:
1. Using the internal UART to USB of the node. Note that this will disable the node's serial interface.
2. Using an external UART to USB cable. Note that this approach requires soldering the cables to the UART3 TX and RX lines (TP28 and TP29), and removing U12 (optional, but needs to be tested).

To compile the FW for option 1 run the following commad:
```
make clean && make debug USE_FAKE_ACCELEROMETER=INTERNAL PRODUCT=DYN USE_G7_BRD_VER=2 -j6
```

To compile the FW for option 2 run the following command:
```
make clean && make debug USE_FAKE_ACCELEROMETER=EXTERNAL PRODUCT=DYN USE_G7_BRD_VER=2 -j6
```


## Development environment

In order to execute the component locally, run the following commands:

```
sudo pip install virtualenv
virtualenv --python=python3 .virtualenv
source .virtualenv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running
A normal execution would look like this:
```
python3 -m dyn_injector.main -i ~/dynamic_data.csv -c /dev/ttyUSB0
```

To see the full options listing, execute:
```
python3 -m dyn_injector.main -h
```
## Simulated data

The application accepts a CSV with 3 columns, one for each axis. Note that each row contains all 3 axis values, if one is missing, the application will throw an error.

The values are scaled floats in g. The values will be transformed to raw values internally before being sent to the node.

Example:
```
x ,y, z
-0.0326080322265625,4009.607177734375,334.45294189453125
0.009876251220703125,0.7538873553276062,309.1700439453125
-0.17077255249023438,0.37183907628059387,286.9229431152344
-0.27472686767578125,0.20231695473194122,266.578857421875
[...]
```
