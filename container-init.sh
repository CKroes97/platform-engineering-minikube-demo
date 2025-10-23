#!/bin/bash

set -e

usage() {
    echo "Usage: container-init.sh"
}

$RUNNER_USER="runner"

# Prompt user for inputs
read -p "Enter GitHub Runner Token: " GITHUB_RUNNER_TOKEN
read -s -p "Enter password for $RUNNER_USER: " RUNNER_PASS

# Validate inputs
if [[ -z "$GITHUB_RUNNER_TOKEN" || -z "$RUNNER_PASS" ]]; then
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
sudo chown "$RUNNER_USER:$RUNNER_USER" "setup_runner.sh"
sudo chmod +x "setup_runner.sh"

# Execute the script as the new user
sudo runuser -p "$RUNNER_USER" -c "bash $(dirname $0)/setup_runner.sh '$GITHUB_RUNNER_TOKEN' '$RUNNER_USER'"
