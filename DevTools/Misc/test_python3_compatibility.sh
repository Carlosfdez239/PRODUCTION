#!/bin/bash

# Define the directory containing the Python scripts.
BIN_DIR=$1
SCRIPT_DIR=$2

# Log file for storing the output.
LOG_FILE="python3_test_results.log"

# Counter for successful and failed script counts.
TOTAL_COUNT=0
SUCCESS_COUNT=0
FAIL_COUNT=0

cd $SCRIPT_DIR

# ANSI color codes
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NO_COLOR='\033[0m'

# Loop through each python script in the directory.
for script in *.py; do

    echo -e "Testing: ${YELLOW} ${script}...${NO_COLOR}"

    # Run the script in the background with xvfb-run, time out after 1 second
    xvfb-run -a timeout 0.5s ../${BIN_DIR}/python "${script}" &> /dev/null
    exit_status=$?

    # Check if timeout occurred
    if [ $exit_status -eq 124 ]; then
        echo -e "${GREEN}${script}: Success.${NO_COLOR}" | tee -a "${LOG_FILE}"
        ((SUCCESS_COUNT++))
    elif [ $exit_status -eq 0 ]; then
        echo -e "${GREEN}${script}: Success.${NO_COLOR}" | tee -a "${LOG_FILE}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}${script}: Fail (error code: $exit_status)${NO_COLOR}" | tee -a "${LOG_FILE}"
        ((FAIL_COUNT++))
    fi
    ((TOTAL_COUNT++))
done

cd ..
# Final report
# Calculate the percentage of failed tests
if [ $TOTAL_COUNT -gt 0 ]; then
    PERCENT_SUCCESS=$(echo "scale=2; ($SUCCESS_COUNT/$TOTAL_COUNT)*100" | bc)
    echo -e "${NO_COLOR}Total tests: $TOTAL_COUNT" | tee -a "${LOG_FILE}"
    echo -e "Success: $SUCCESS_COUNT" | tee -a "${LOG_FILE}"
    echo -e "Failures: $FAIL_COUNT" | tee -a "${LOG_FILE}"
    echo -e "Percentage of tests succeeded: $PERCENT_SUCCESS%" | tee -a "${LOG_FILE}"
else
    echo "No tests were found."
fi

