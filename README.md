# platform-engineering-minikube-demo
Implementation of the platform engineering reference architecture for OpenShift but then just with regular Kubernetes running on Minikube for demo purposes.

V2 also adds an LLM server, firewall and MCP.

Designed for running on WSL with Fedora-41 as OS.

Scripts and resulting Github Runner have extensive access to the container and will install and write lots of files in lots of directories.
Do not run on WSL instance that is also used for other purposes.

Security shortcuts taken for easy and quick development. Do not expose WSL container to the wider network.

Developed for Fedora 41 running on WSL

Usage:
- Make sure you are running the latest version of WSL (`wsl --update`)
- Run `install-container.ps1` 
- Clone repo (again) in  fedora 41 instance
- run init.sh to add a github runner (token can be gotten from github repo settings > actions )
    Note: this adds a dedicated Linux user with paswordless Sudo rights.
- Run the "configure_host.yaml" action in Github actions
- Run the "deploy.yaml" action in Github actions
- Add Python webserver scripts to the "webservices" folder
- Profit

When facing issues building the docker images and pushing them to the repository
it might help to log in to the WSL instance and run `sudo docker login localhost:30080`

Desired end state architecture:
![architecture overview](docs/architecture.png)