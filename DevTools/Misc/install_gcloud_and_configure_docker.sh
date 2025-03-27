#!/bin/bash

# Check if gcloud is installed
if ! command -v gcloud &>/dev/null; then
    echo "Google Cloud SDK (gcloud) is not installed. Installing gcloud..."
    # Add the Google Cloud SDK installation steps from the previous script
    # ...
    echo "Adding Google Cloud SDK repository..."
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

    # Import the Google Cloud public key
    echo "Importing Google Cloud public key..."
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

    # Update package list and install gcloud
    echo "Updating package list and installing Google Cloud SDK (gcloud)..."
    sudo apt update
    sudo apt install google-cloud-sdk

    # Authenticate with your Google Cloud account (replace with your own authentication method)

    echo "Google Cloud SDK (gcloud) installation completed."
    # Authenticate with your Google Cloud account (replace with your own authentication method)
    gcloud auth login
fi

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Configure Docker to authenticate with Google Cloud Container Registry (gcr.io)
echo "Configuring Docker to authenticate with Google Cloud Container Registry (gcr.io)..."
gcloud auth configure-docker

# Pull the Docker image from Google Cloud Container Registry
echo "Pulling Docker image from Google Cloud Container Registry..."
docker pull eu.gcr.io/engineering-test-197116/fw_develdockerimage

echo "Docker image has been pulled successfully."