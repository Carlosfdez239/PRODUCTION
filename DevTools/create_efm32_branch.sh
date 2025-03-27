#!/bin/bash
#Script for create a new branch.
#$1 name of the branch
#Does checkout and creates a directory with the base and code to develop

echo "Define the user name and delete this line!!!" & exit 1
DEVELOPER_NAME="xxxxxxxx" # put here your username
DATE=`date +%F`
BRANCH_NAME="$DATE-$DEVELOPER_NAME-$1"
SVN_BRANCH_URL_BASE="https://www.ac.upc.edu/projects/wsn/svn/wsn/Firmware_EFM32/Platform_EFM32/Platform_EFM32_Branches/"
SVN_MAIN_URL="https://www.ac.upc.edu/projects/wsn/svn/wsn/Firmware_EFM32/Platform_EFM32/Platform_EFM32_Trunk/"
SVN_BRANCH_URL="$SVN_BRANCH_URL_BASE$BRANCH_NAME"
DIR="EFM32_dev_$1"

mkdir $DIR

if [ $# -ne 1 ]
then
    echo "Error few arguments"
    exit
fi
echo $BRANCH_NAME
cd $DIR
svn copy $SVN_MAIN_URL $SVN_BRANCH_URL -m "Branch $1"
svn checkout $SVN_BRANCH_URL dev

cp -r dev dev_base

