#!/bin/bash

set -e

usage() {
    echo "Usage: setup.sh --github-runner-token <token> [options]"
    echo "Required:"
    echo "  --github-runner-token <token>    GitHub Actions runner token"
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --github-runner-token) GITHUB_RUNNER_TOKEN="$2"; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown parameter: $1"; usage ;;
    esac
    shift
done

if [[ -z "$GITHUB_RUNNER_TOKEN" ]]; then
    echo "Error: --github-runner-token is required."
    usage
fi

cd ~

# install github runner
mkdir actions-runner && cd actions-runner

curl -o actions-runner-linux-x64-2.323.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-linux-x64-2.323.0.tar.gz

echo "0dbc9bf5a58620fc52cb6cc0448abcca964a8d74b5f39773b7afcad9ab691e19  actions-runner-linux-x64-2.323.0.tar.gz" | shasum -a 256 -c

tar xzf ./actions-runner-linux-x64-2.323.0.tar.gz

./config.sh --url https://github.com/CKroes97/platform-engineering-minikube-demo --token $GITHUB_RUNNER_TOKEN

sudo ./svc.sh install

sudo ./svc.sh start

# create terraform dir
sudo mkdir /var/lib/terraform
sudo chown $USER:$USER /var/lib/terraform
sudo chmod 755 /var/lib/terraform