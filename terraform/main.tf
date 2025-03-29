resource "kubernetes_namespace" "registry_namespace" {
  metadata {
    name = "docker-registry"
  }
}

resource "helm_release" "harbor" {
  name       = "harbor"
  namespace  = kubernetes_namespace.registry_namespace.metadata[0].name
  repository = "https://helm.goharbor.io"
  chart      = "harbor"
  version    = "2.12.2"  # Specify the desired version
}

