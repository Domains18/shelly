#!/bin/bash

# Installation script for Shelly

set -e

echo "Installing Shelly..."

pip install -r requirements.txt

pip install -e .

echo "Installation completed."

