resource "kubernetes_namespace" "registry_namespace" {
  metadata {
    name = "docker-registry"
  }
}

resource "helm_release" "harbor" {
  name      = "harbor"
  namespace = kubernetes_namespace.registry_namespace.metadata[0].name
  repository= "https://helm.goharbor.io"
  chart     = "harbor"
  values = [templatefile("helm_values/harbor.yaml", {
    HARBOR_URL      = var.harbor_url
    HARBOR_USERNAME = var.harbor_username
    HARBOR_PASSWORD = var.harbor_password
  })]
}

resource "kubernetes_secret" "harbor_credentials" {
  metadata {
    name      = "harbor-credentials"
    namespace = kubernetes_namespace.registry_namespace.metadata[0].name
  }

  data = {
    HARBOR_URL      = var.harbor_url
    HARBOR_USERNAME = var.harbor_username
    HARBOR_PASSWORD = var.harbor_password
  }

  type = "Opaque"
}

resource "kubernetes_deployment" "harbor_cli" {
  metadata {
    name      = "harbor-cli"
    namespace = kubernetes_namespace.registry_namespace.metadata[0].name
    labels = {
      app = "harbor-cli"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "harbor-cli"
      }
    }

    template {
      metadata {
        labels = {
          app = "harbor-cli"
        }
      }

      spec {
        container {
          name  = "hcli"
          image = "goharbor/harbor-cli:latest"

          command = ["/bin/sh", "-c", "sleep infinity"]

          env_from {
            secret_ref {
              name = kubernetes_secret.harbor_credentials.metadata[0].name
            }
          }
        }
      }
    }
  }
}


# Terraform Variables for GitHub Secrets
variable "harbor_url" {
  type = string
}
variable "harbor_username" {
  type = string
}
variable "harbor_password" {
  type = string
}