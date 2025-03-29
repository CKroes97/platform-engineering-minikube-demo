# platform-engineering-minikube-demo
Implementation of the platform engineering reference architecture for OpenShift but then just with regular Kubernetes running on Minikube for demo purposes


Requires amd64 platform

Usage:
- Fork repo
- run init.sh to add a github runner (token can be gotten from github repo settings > actions )
    Note: this adds a dedicated Linux user with paswordless Sudo rights.
- Run the "deploy.yaml" action
- Profit