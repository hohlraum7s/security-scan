# 04 - Baseline Architecture & Configuration

This document specifies the concrete configuration baseline, manifests, and technical architecture for deploying the Trivy Operator on RKE2 in an air-gapped environment.

---

## 1. System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Air-Gapped RKE2 Cluster                                                          │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ Namespace: trivy-system                                                    │  │
│  │                                                                            │  │
│  │  ┌─────────────────────────┐               ┌────────────────────────────┐  │  │
│  │  │ Trivy Operator Pod      ├──────────────►│ Scan Job Pod (Ephemeral)   │  │  │
│  │  │ (Watches K8s API)       │ Spawns        │ • Image: trivy:0.52.0      │  │  │
│  │  └────────────┬────────────┘               └─────────────┬──────────────┘  │  │
│  │               │                                          │                 │  │
│  │               │ Writes Reports                           │ Pulls DB        │  │
│  │               ▼                                          ▼                 │  │
│  │  ┌─────────────────────────┐               ┌────────────────────────────┐  │  │
│  │  │ K8s Custom Resources    │               │ Local Harbor OCI Registry  │  │  │
│  │  │ • VulnerabilityReport   │               │ • mirror/trivy-db:2        │  │  │
│  │  │ • ConfigAuditReport     │               │ • security/trivy:0.52.0    │  │  │
│  │  │ • RbacAssessmentReport  │               └────────────────────────────┘  │  │
│  │  └─────────────────────────┘                                               │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Air-Gapped OCI Database Synchronization Baseline

Aqua Security publishes the Trivy vulnerability database as an OCI artifact. In an air-gapped setup, the database must be pulled from upstream, passed through the data diode, and stored in Harbor as an OCI artifact.

### Target OCI Registries & References
* **Upstream Trivy DB**: `ghcr.io/aquasecurity/trivy-db:2`
* **Internal Harbor Mirror**: `harbor.internal.domain/mirror/aquasecurity/trivy-db:2`
* **Upstream Java DB**: `ghcr.io/aquasecurity/trivy-java-db:1`
* **Internal Harbor Java DB**: `harbor.internal.domain/mirror/aquasecurity/trivy-java-db:1`

---

## 3. Helm Values Baseline (`values-airgap.yaml`)

This configuration override file adapts the standard `trivy-operator` chart for complete offline execution.

```yaml
# values-airgap.yaml - Trivy Operator Air-Gapped Production Baseline

image:
  registry: harbor.internal.domain
  repository: security/trivy-operator
  tag: "0.22.0"
  pullPolicy: IfNotPresent

trivyOperator:
  scanJobTimeout: "15m"
  scanJobsConcurrentLimit: 3
  metrics:
    enabled: true

trivy:
  mode: Standalone
  image:
    registry: harbor.internal.domain
    repository: security/trivy
    tag: "0.52.0"
  
  # Air-Gapped Local OCI DB Endpoints (Trivy appends schema tag :2 for dbRepository and :1 for javaDbRepository automatically)
  dbRepository: harbor.internal.domain/mirror/aquasecurity/trivy-db
  javaDbRepository: harbor.internal.domain/mirror/aquasecurity/trivy-java-db
  
  # Strict Offline Enforcement
  offlineScan: true
  
  # Scan Options
  severity: "CRITICAL,HIGH,MEDIUM"
  ignoreUnfixed: false

  # Resource Allocation for Ephemeral Scan Pods
  resources:
    requests:
      cpu: "100m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"

# Operator Scopes
operator:
  builtInTrivyServer: false
  scannerReportTTL: "24h" # Automatically prune stale scan reports

# Pod Security & Placement for RKE2 Control Plane / Worker Nodes
nodeSelector:
  kubernetes.io/os: linux

tolerations:
  - key: "CriticalAddonsOnly"
    operator: "Exists"
  - key: "node-role.kubernetes.io/control-plane"
    operator: "Exists"
    effect: "NoSchedule"
```

---

## 4. ArgoCD Application Baseline (`trivy-operator-app.yaml`)

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
        - values-airgap.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: trivy-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

## 5. Generated Custom Resource Definitions (CRDs)

Once deployed, Trivy Operator populates the following K8s CRDs in scanned namespaces:

1. `vulnerabilityreports.aquasecurity.github.io`: Per-workload image vulnerability scan results (CVE ID, CVSS score, fixed version).
2. `configauditreports.aquasecurity.github.io`: Manifest security audit (runAsNonRoot, privilegeEscalation, capabilities).
3. `rbacassessmentreports.aquasecurity.github.io`: Overprivileged RBAC bindings analysis.
4. `exposedsecretreports.aquasecurity.github.io`: Detection of committed hardcoded secrets.
