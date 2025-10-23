#!/bin/bash

set -e

GITHUB_RUNNER_TOKEN=$1

if [[ -z "$GITHUB_RUNNER_TOKEN" ]]; then
    echo "Error: GitHub Runner Token is required."
    exit 1
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