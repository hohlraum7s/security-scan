# 09 - ArgoCD Helm Deployment Guide

This guide provides step-by-step instructions for deploying the **Trivy Operator** and the **Prometheus/Grafana Security Monitoring Stack** declaratively using **ArgoCD** and **Helm** in an air-gapped RKE2 cluster.

---

## 1. GitOps Directory Structure

All Kubernetes manifests, Helm values, and ArgoCD application definitions must be stored in your internal Git repository (e.g. GitLab / Gitea) using the following directory layout:

```text
git-repo/
└── infrastructure/
    └── security-stack/
        ├── README.md
        ├── apps/
        │   ├── trivy-operator-app.yaml      # ArgoCD Application for Trivy Operator
        │   └── monitoring-app.yaml          # ArgoCD Application for Prometheus/Grafana
        └── values/
            ├── trivy-values-airgap.yaml     # Production values override for Trivy Operator
            ├── prometheus-values.yaml       # Production values override for Prometheus/Alertmanager
            ├── security-dashboard-cm.yaml   # ConfigMap for Grafana Dashboard
            └── trivy-alerts-rule.yaml       # PrometheusRule CRD for Alertmanager
```

---

## 2. Registering Internal Repositories in ArgoCD

In an air-gapped network, ArgoCD must pull Helm charts from **Nexus** and container images from **Harbor**.

### A. Add Internal Helm Repository to ArgoCD
Run the following `argocd` CLI command (or add to your ArgoCD `repositories` secret):

```bash
# Register Nexus Helm repository in ArgoCD
argocd repo add https://nexus.internal.domain/repository/helm-charts \
  --type helm \
  --name nexus-helm-repo \
  --username "argocd-reader" \
  --password "SecretPassword123"
```

### B. Register Internal Git Repository in ArgoCD
```bash
# Register internal Git repository containing your manifests
argocd repo add https://git.internal.domain/devops/k8s-security-stack.git \
  --username "argocd-git" \
  --password "GitToken123"
```

---

## 3. ArgoCD Application Manifests

### A. Trivy Operator ArgoCD Application (`apps/trivy-operator-app.yaml`)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: trivy-operator
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: 'https://nexus.internal.domain/repository/helm-charts'
    chart: trivy-operator
    targetRevision: 0.22.0
    helm:
      valueFiles:
        - '$values/infrastructure/security-stack/values/trivy-values-airgap.yaml'
  # Multiple sources feature allows referencing values from internal Git repo while pulling chart from Nexus
  sources:
    - repoURL: 'https://nexus.internal.domain/repository/helm-charts'
      chart: trivy-operator
      targetRevision: 0.22.0
      helm:
        valueFiles:
          - '$values/infrastructure/security-stack/values/trivy-values-airgap.yaml'
    - repoURL: 'https://git.internal.domain/devops/k8s-security-stack.git'
      targetRevision: HEAD
      ref: values
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: trivy-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
      - SkipDryRunOnMissingResource=true
```

### B. Security Monitoring Stack ArgoCD Application (`apps/monitoring-app.yaml`)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: security-monitoring-stack
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  sources:
    - repoURL: 'https://nexus.internal.domain/repository/helm-charts'
      chart: kube-prometheus-stack
      targetRevision: 61.3.0
      helm:
        valueFiles:
          - '$values/infrastructure/security-stack/values/prometheus-values.yaml'
    - repoURL: 'https://git.internal.domain/devops/k8s-security-stack.git'
      targetRevision: HEAD
      ref: values
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: monitoring
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

---

## 4. Deployment Execution Steps

### Step 1: Commit Manifests to Internal Git
Push your `apps/` and `values/` files to `https://git.internal.domain/devops/k8s-security-stack.git`.

### Step 2: Apply ArgoCD Applications
Execute `kubectl` to register the applications with ArgoCD on the RKE2 cluster:

```bash
# Apply Trivy Operator ArgoCD Application
kubectl apply -f infrastructure/security-stack/apps/trivy-operator-app.yaml -n argocd

# Apply Monitoring Stack ArgoCD Application
kubectl apply -f infrastructure/security-stack/apps/monitoring-app.yaml -n argocd
```

### Step 3: Trigger & Monitor ArgoCD Sync

```bash
# Watch ArgoCD sync progress
argocd app get trivy-operator
argocd app sync trivy-operator

# Check sync status of security-monitoring-stack
argocd app get security-monitoring-stack
```

---

## 5. Troubleshooting Air-Gapped ArgoCD Deployments

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`rpc error: repo connection timeout`** | ArgoCD cannot resolve or reach Nexus/Git internal domain. | Check CoreDNS resolution inside `argocd-repo-server` pod. |
| **`Helm chart not found`** | Chart `trivy-operator-0.22.0.tgz` missing in Nexus. | Re-run diode sync script to push Helm package across diode into Nexus. |
| **`CRD conversion webhook error`** | ArgoCD dry-run failed due to missing CRDs. | Ensure `SkipDryRunOnMissingResource=true` is set in `syncOptions`. |
| **`ImagePullBackOff` on Trivy pods** | Harbor image pull secret missing in target namespace. | Deploy `harbor-registry-secret` to `trivy-system` namespace. |
