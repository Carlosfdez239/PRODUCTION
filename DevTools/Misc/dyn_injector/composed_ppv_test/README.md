# Injection tests for PPV

This script generates the data to be injected using the DYN_INJECTOR tool to test the DIN algorithm, particularly to test the composed PPV calculation.

## Usage
#### Compile the node FW
Before injecting the data it is important to set the desired config, as the injection FW disables the USB for configurations.
Example config json:
```
{'type': 'setVibrationRegulationCfgV1', 'outputParameterCfg': {'samplingFrequency': 1000, 'highPassFilter': 62.084, 'samplesToDiscard': 2539, 'dynamicRange': '0-30 mm/s', 'wakeUpThreshold': 10.0, 'transmissionThreshold': 20.0, 'samplesInWindow': 2048, 'stoppageTime': 10, 'maxWindowsPerEvent': 30, 'shortEventNumWindows': 5, 'lowPassFilterCutOff': 1000, 'vibrationEventThreshold': 20.0, 'rawDataStorageSchedulingMode': 'Disabled', 'rawDataStorageOperatingMode': 'All axes'}, 'outputParameter': 'PPV', 'cfgVersion': 1, 'AlertMode': 0}
```

 #### Generate the test .csv file:
```
python composed_ppv_tester.py -t N
```

where N is the test number.

The following tests are defined:
 -  0 - Test used to translate node debug prints to correct units.
 -  1 - Test used to calibrate the injection gain.
 -  2 - Test uses a random signal with the maximum on the Y axis.
 -  3 - Test uses a random signal with the maximum on the X axis and the X and Y axis aligned.
 -  4 - Test uses a random signal with the maximum on the Z axis and the X and Z axis aligned.
 -  5 - Test uses a random signal with the maximum on the Z axis and the Y and Z axis aligned.
 -  6 - Test uses a train acceleration signal with the maximum on the X axis and none of the axis aligned.
 -  7 - Test uses a train acceleration signal with the maximum on the Y axis and none of the axis aligned.
 -  8 - Test uses a train acceleration signal with the maximum on the Z axis and none of the axis aligned.

#### Inject the data in the node following the steps of its readme.md
file: https://bitbucket.org/worldsensing_traffic/loadsensingg7/src/development/DevTools/Misc/dyn_injector/

#### Wait for the injected event to end
Once the event ends, the debug logs should show the following:
```
******************
Summary event:
- #Windows: 10
- Composed PPV: 1814
- X:  PPV_Freq: 26367188, PPV_Val: 1319, PPV_Time: 4294967295
- Y:  PPV_Freq: 26367188, PPV_Val: 1814, PPV_Time: 4294967295
- Z:  PPV_Freq: 26367188, PPV_Val: 1237, PPV_Time: 4294967295
******************
```

#### Use test 0 to parse the debug outputs:
Test number 0 runs a script to parse the debug logs and prints the PPV values and frequencies in the correct units.

## Results:
### Test 1
Results:
```
------ Obtained Results ------
  -) X: ppv_value = 2.265344, ppv_frequency = 1.0
  -) Y: ppv_value = 2.265344, ppv_frequency = 1.0
  -) Z: ppv_value = 2.265344, ppv_frequency = 1.0
  -) Combined: ppv_value = 3.923691
```

### Test 2
Expectation:
```
Test number:  2
------ Expected Results ------
  -) X: ppv_value = 0.0013368494157760002, ppv_frequency = 26.85546875
  -) Y: ppv_value = 0.0018381679466920001, ppv_frequency = 26.85546875
  -) Z: ppv_value = 0.00125329632729, ppv_frequency = 26.85546875
  -) Combined: ppv_value = 0.0018389581554795233
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.001319, ppv_frequency = 26.367188
  -) Y: ppv_value = 0.001814, ppv_frequency = 26.367188
  -) Z: ppv_value = 0.001237, ppv_frequency = 26.367188
  -) Combined: ppv_value = 0.001814
```

### Test 3
Expectation:
```
Test number:  3
------ Expected Results ------
  -) X: ppv_value = 0.00334212353944, ppv_frequency = 26.85546875
  -) Y: ppv_value = 0.0018381679466920001, ppv_frequency = 26.85546875
  -) Z: ppv_value = 0.00125329632729, ppv_frequency = 26.85546875
  -) Combined: ppv_value = 0.0038144369357883258
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.003298, ppv_frequency = 26.367188
  -) Y: ppv_value = 0.001814, ppv_frequency = 26.367188
  -) Z: ppv_value = 0.001237, ppv_frequency = 26.367188
  -) Combined: ppv_value = 0.003764
```

### Test 4
Expectation:
```
------ Expected Results ------
  -) X: ppv_value = 0.00167106176972, ppv_frequency = 26.85546875
  -) Y: ppv_value = 0.0013368494157760002, ppv_frequency = 26.85546875
  -) Z: ppv_value = 0.0018381679466920001, ppv_frequency = 26.85546875
  -) Combined: ppv_value = 0.0024845045583053397
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.001649, ppv_frequency = 26.367188
  -) Y: ppv_value = 0.001319, ppv_frequency = 26.367188
  -) Z: ppv_value = 0.001814, ppv_frequency = 26.367188
  -) Combined: ppv_value = 0.002452
```

### Test 5
Expectation:
```
Test number:  5
------ Expected Results ------
  -) X: ppv_value = 0.00167106176972, ppv_frequency = 26.85546875
  -) Y: ppv_value = 0.0013368494157760002, ppv_frequency = 26.85546875
  -) Z: ppv_value = 0.0018381679466920001, ppv_frequency = 26.85546875
  -) Combined: ppv_value = 0.002273389480979667
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.001649, ppv_frequency = 26.367188
  -) Y: ppv_value = 0.001319, ppv_frequency = 26.367188
  -) Z: ppv_value = 0.001814, ppv_frequency = 26.367188
  -) Combined: ppv_value = 0.002243
```

### Test 6
Expectation:
```
Test number:  6
------ Expected Results ------
  -) X: ppv_value = 0.4503920373252667, ppv_frequency = 0.9765625
  -) Y: ppv_value = 0.11011581208461638, ppv_frequency = 0.9765625
  -) Z: ppv_value = 0.014701723943558053, ppv_frequency = 22.94921875
  -) Combined: ppv_value = 0.45961412077895375
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.459637, ppv_frequency = 1.0
  -) Y: ppv_value = 0.12204, ppv_frequency = 1.0
  -) Z: ppv_value = 0.014933, ppv_frequency = 22.460938
  -) Combined: ppv_value = 0.472871
```

* Note that the node limits the minimum frequency to 1. Thus frequencies below this value are reported as 1.

### Test 7
Expectation:
```
Test number:  7
------ Expected Results ------
  -) X: ppv_value = 0.11011581208461638, ppv_frequency = 0.9765625
  -) Y: ppv_value = 0.4503920373252667, ppv_frequency = 0.9765625
  -) Z: ppv_value = 0.014701723943558053, ppv_frequency = 22.94921875
  -) Combined: ppv_value = 0.45961412077895375
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.12204, ppv_frequency = 1.0
  -) Y: ppv_value = 0.459637, ppv_frequency = 1.0
  -) Z: ppv_value = 0.014933, ppv_frequency = 22.460938
  -) Combined: ppv_value = 0.472871
```

### Test 8
Expectation:
```
Test number:  8
------ Expected Results ------
  -) X: ppv_value = 0.014701723943558053, ppv_frequency = 22.94921875
  -) Y: ppv_value = 0.11011581208461638, ppv_frequency = 0.9765625
  -) Z: ppv_value = 0.4503920373252667, ppv_frequency = 0.9765625
  -) Combined: ppv_value = 0.45961412077895375
```

Results:
```
------ Obtained Results ------
  -) X: ppv_value = 0.014933, ppv_frequency = 22.460938
  -) Y: ppv_value = 0.12204, ppv_frequency = 1.0
  -) Z: ppv_value = 0.459637, ppv_frequency = 1.0
  -) Combined: ppv_value = 0.472871
```