# 02 - Prerequisites & System Dependencies

Prior to initiating the deployment of the air-gapped security scanner, all system, network, and artifact prerequisites listed below must be verified and satisfied.

---

## 1. RKE2 Cluster Prerequisites

| Component | Minimum Requirement | Notes / Verification |
| :--- | :--- | :--- |
| **RKE2 Version** | `v1.26.x` or higher | Run `kubectl version` |
| **Cluster Topology** | Standalone RKE2 Cluster | Control Plane & Worker nodes initialized |
| **Node Resources** | CPU: 2 Cores free<br>Memory: 4 GB RAM free | For running scanner operator & transient scan jobs |
| **Default StorageClass** | Persistent Storage available | Required if scan reports/caches require PVCs |
| **Cluster Ingress / CoreDNS** | Internal DNS operational | `harbor.internal.domain` must resolve inside pods |

---

## 2. Internal Registry & Artifact Store Setup

The following internal endpoints must be operational and accessible by the RKE2 cluster nodes:

### A. Harbor Registry (`harbor.internal.domain`)
- **Container Image Mirroring**:
  - Project `security`: Contains `trivy-operator:0.22.0` and `trivy:0.52.0`.
- **OCI Database Mirroring**:
  - Project `mirror/aquasecurity`: Receives OCI artifacts for vulnerability databases:
    - `harbor.internal.domain/mirror/aquasecurity/trivy-db:2`
    - `harbor.internal.domain/mirror/aquasecurity/trivy-java-db:1`
- **Authentication**: `imagePullSecrets` created in the `trivy-system` namespace if Harbor projects are private.

### B. Nexus Repository (`nexus.internal.domain`)
- **Helm Repository**:
  - Hosted / Proxy Helm repository containing the `trivy-operator` chart (`v0.22.0`).

---

## 3. Unidirectional Data Diode Pipeline Specs

The diode sync process operates across the security boundary to push updated artifacts into the air gap:

```
[ Connected Staging Zone ]               [ Data Diode ]           [ Air-Gapped Network ]
┌─────────────────────────┐               ┌───────────┐           ┌─────────────────────┐
│ 1. Download Trivy DB    │               │  One-Way  │           │ 3. Receive OCI DB   │
│    (ghcr.io OCI image)  ├──────────────►│ Transfer  ├──────────►│    Push to Harbor   │
│ 2. Download App Images  │               │ Hardware  │           │    Internal Registry│
└─────────────────────────┘               └───────────┘           └─────────────────────┘
```

* **Diode Sync Schedule**: Recommended daily or bi-weekly sync of the `trivy-db:2` OCI image.
* **Sync Verification**: Verify Harbor contains the updated `trivy-db:2` manifest tag.

---

## 4. GitOps & Ansible Prerequisites

### A. Git Repository
- Git repository hosted on internal Git server (e.g. GitLab / Gitea) accessible by ArgoCD.
- Repository structure containing:
  - `apps/trivy-operator/values-airgap.yaml`
  - `apps/trivy-operator/application.yaml`

### B. ArgoCD Controller
- ArgoCD deployed on the RKE2 cluster with permissions to manage CRDs and create `trivy-system` namespace resources.

### C. Ansible Control Node
- Ansible `core 2.14+` installed on deployment host.
- Access to RKE2 cluster via `KUBECONFIG`.
- Installed collections: `kubernetes.core`, `community.general`.
