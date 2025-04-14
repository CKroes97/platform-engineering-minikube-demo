# platform-engineering-minikube-demo
Implementation of the platform engineering reference architecture for OpenShift but then just with regular Kubernetes running on Minikube for demo purposes.

Security shortcuts taken for easy and quick development. Do not expose WSL container to the wider network.

Do not run on WSL instance that is also used for other purposes.

Developed for Ubuntu 24.04 running on WSL

Usage:
- Fork repo
- run init.sh to add a github runner (token can be gotten from github repo settings > actions )
    Note: this adds a dedicated Linux user with paswordless Sudo rights.
- Run the "configure_host.yaml" action
- Run the "deploy.yaml" action
- Profit