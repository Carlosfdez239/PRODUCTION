#!/bin/bash

# Repo config variable
REPO_NAME="fwcontinuousintegration"
REPO_URL="git@bitbucket.org:worldsensing_traffic/${REPO_NAME}.git"
DOCKERFILES_DIR="Dockerfiles/fw_develdockerimage"

# GCC Version
GCC_VERSION="10.3"
RELEASE_DATE="2021.10"
SEARCH_PATTERN="gcc-arm-none-eabi-${GCC_VERSION}-${RELEASE_DATE}" # search pattern to search for existence of archive on repo

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target-directory>"
    exit 1
fi

TARGET_DIR=$1
# Check the installed version of arm-none-eabi-gcc
if ${TARGET_DIR}/bin/arm-none-eabi-gcc --version 2>/dev/null | grep -q "${GCC_VERSION}-${RELEASE_DATE}"; then
    echo "ARM GCC version ${GCC_VERSION} is already installed."
    exit 0
else
    echo "Installing ARM GCC version 10.3 from internal repo ${REPO_NAME}"
    if git clone "$REPO_URL"; then
        # Check if the target directory exists, create if not
        if [[ ! -d "$TARGET_DIR" ]]; then
            sudo mkdir -p "$TARGET_DIR"
        fi

    # Find and extract the matching toolchain archive
    echo "Unpacking ARM GCC Embedded Toolchain to $TARGET_DIR"
    find "${REPO_NAME}/${DOCKERFILES_DIR}" -name "*$SEARCH_PATTERN*.tar.bz2" -exec sudo tar -xvjf {} -C "$TARGET_DIR" --strip-components=1 \;
    # Delete repo folder
    rm -rf "$REPO_NAME"
    echo "ARM GCC Embedded Toolchain v$GCC_VERSION has been installed to $TARGET_DIR"
    else
        echo "Failed to clone $REPO_NAME"
    fi
fi 

