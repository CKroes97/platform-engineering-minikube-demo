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

provider "kubernetes" {
  config_path    = "/home/runner/.kube/config"
  config_context = "minikube"
}