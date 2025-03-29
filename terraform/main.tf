resource "kubernetes_namespace" "registry_namespace" {
  metadata {
    name = "docker-registry"
  }
}

resource "helm_release" "harbor" {
  name       = "harbor"
  namespace  = kubernetes_namespace.registry_namespace.metadata.name
  repository = "https://helm.goharbor.io"
  chart      = "harbor"
  version    = "2.9.0"  # Specify the desired version
}

