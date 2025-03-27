terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
  backend "local" {
   path = "/var/lib/terraform/terraform.tfstate"
  }
}



provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

resource "kubernetes_namespace" "registry_namespace" {
  metadata {
    name = "docker-registry"
  }
}