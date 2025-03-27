#!/bin/bash

set -e

usage() {
    echo "Usage: setup.sh"
}

# Prompt user for inputs
read -p "Enter GitHub Runner Token: " GITHUB_RUNNER_TOKEN
read -p "Enter Unix username for GitHub Runner: " RUNNER_USER
read -s -p "Enter password for $RUNNER_USER: " RUNNER_PASS

# Validate inputs
if [[ -z "$GITHUB_RUNNER_TOKEN" || -z "$RUNNER_USER" || -z "$RUNNER_PASS" ]]; then
    echo "Error: All inputs are required."
    exit 1
fi

if ! id "$RUNNER_USER" &>/dev/null; then
    echo "Creating user $RUNNER_USER..."
    sudo useradd -m -s /bin/bash "$RUNNER_USER"
    echo "$RUNNER_USER:$RUNNER_PASS" | sudo chpasswd
fi

# Grant passwordless sudo access
echo "$RUNNER_USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$RUNNER_USER

# Change ownership & permissions
sudo chown "$RUNNER_USER:$RUNNER_USER" "./setup_runner.sh"
sudo chmod +x "./setup_runner.sh"

# Execute the script as the new user
sudo runuser -l "$RUNNER_USER" -c "bash ./setup_runner.sh '$GITHUB_RUNNER_TOKEN'"
