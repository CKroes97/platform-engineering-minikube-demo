resource "kubernetes_namespace" "registry_namespace" {
  metadata {
    name = "docker-registry"
  }
}

resource "kubernetes_persistent_volume_claim" "registry_pvc" {
  metadata {
    name      = "registry-pvc"
    namespace = kubernetes_namespace.registry_namespace.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
  }
}

resource "kubernetes_secret" "registry_auth_secret" {
  metadata {
    name      = "registry-auth-secret"
    namespace = kubernetes_namespace.registry_namespace.metadata[0].name
  }

  data = {
    "htpasswd" = file("/etc/platform-registry/htpasswd")  # Directly reference the file
  }

  type = "Opaque"
}


resource "kubernetes_deployment" "registry" {
  metadata {
    name      = "registry"
    namespace = kubernetes_namespace.registry_namespace.metadata[0].name
    labels = {
      app = "registry"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "registry"
      }
    }

    template {
      metadata {
        labels = {
          app = "registry"
        }
      }

      spec {
        container {
          name  = "registry"
          image = "registry:2"

          port {
            container_port = 5000
          }

          env {
            name  = "REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY"
            value = "/var/lib/registry"
          }

          env {
            name  = "REGISTRY_AUTH_HTPASSWD_REALM"
            value = "Registry"
          }

          env {
            name  = "REGISTRY_AUTH_HTPASSWD_PATH"
            value = "/auth/htpasswd"
          }

          env {
            name  = "REGISTRY_AUTH"
            value = "htpasswd"
          }

          volume_mount {
            name       = "registry-storage"
            mount_path = "/var/lib/registry"
          }

          volume_mount {
            name       = "auth-volume"
            mount_path = "/auth"
            read_only  = true
          }
        }
        
        volume {
          name = "registry-storage"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.registry_pvc.metadata[0].name
          }
        }
        volume {
          name = "auth-volume"
          secret {
            secret_name = kubernetes_secret.registry_auth_secret.metadata[0].name
          }
        }
      }
    }
  }
}




resource "kubernetes_service" "registry" {
  metadata {
    name      = "registry"
    namespace = kubernetes_namespace.registry_namespace.metadata[0].name
  }

  spec {
    selector = {
      app = "registry"
    }

    port {
      protocol    = "TCP"
      port        = 5000
      target_port = 5000
      node_port   = 30080
    }

    type = "NodePort"
  }
}