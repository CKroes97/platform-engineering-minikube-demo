#!/bin/bash

set -e

usage() {
    echo "Usage: setup.sh"
}

# Prompt user for inputs
read -p "Enter GitHub Runner Token: " GITHUB_RUNNER_TOKEN

# Validate inputs
if [[ -z "$GITHUB_RUNNER_TOKEN"]]; then
    echo "Error: All inputs are required."
    exit 1
fi

# Execute the script as the new user
sudo $(dirname $0)/setup_runner.sh '$GITHUB_RUNNER_TOKEN' '$RUNNER_USER'
