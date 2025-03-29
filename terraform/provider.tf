terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
  backend "local" {
   path = "/var/lib/plateng/terraform.tfstate"
  }
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config" # Path to your Kubeconfig file
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}
