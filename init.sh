#!/bin/bash

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

# install github runner
mkdir actions-runner; cd actions-runner

Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-win-x64-2.323.0.zip -OutFile actions-runner-win-x64-2.323.0.zip

if((Get-FileHash -Path actions-runner-win-x64-2.323.0.zip -Algorithm SHA256).Hash.ToUpper() -ne 'e8ca92e3b1b907cdcc0c94640f4c5b23f377743993a4a5c859cb74f3e6eb33ef'.ToUpper()){ throw 'Computed checksum did not match' }

Add-Type -AssemblyName System.IO.Compression.FileSystem ; [System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD/actions-runner-win-x64-2.323.0.zip", "$PWD")

./config.cmd --url https://github.com/CKroes97/platform-engineering-minikube-demo --token $GITHUB_RUNNER_TOKEN

# install terraform
sudo apt install -y gnupg software-properties-common

wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update

sudo apt install terraform

# install kubectl

sudo apt install -y apt-transport-https ca-certificates curl gnupg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubectl

# install minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
minikube start --kubernetes-version=v1.32.0


