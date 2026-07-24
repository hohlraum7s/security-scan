# 05 - Step-by-Step Deployment & Operations Playbook

This playbook provides actionable, step-by-step instructions for installing, configuring, and verifying the air-gapped security scanner stack on an RKE2 cluster.

---

## Deployment Execution Matrix

| Phase | Objective | Tools Used | Responsible Role |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Mirror container images & OCI DB through Diode | Ansible, Skopeo, Oras | Platform / Diode Automation |
| **Phase 2** | Publish Helm chart to Nexus | Helm, Curl | DevOps Engineer |
| **Phase 3** | Commit ArgoCD Application & Helm Values | Git, ArgoCD | GitOps Admin |
| **Phase 4** | Verify execution & scan report CRDs | Kubectl, Trivy CLI | Security / Cluster Admin |

---

## Phase 1: Diode Data Sync (Outside Air-Gap -> Harbor/Nexus)

Execute the following script or Ansible playbook on the **Connected Staging Host** before syncing across the diode into the air-gapped network:

```bash
#!/usr/bin/env bash
set -eo pipefail

# Configuration
HARBOR_SRC="ghcr.io/aquasecurity"
HARBOR_DEST="harbor.internal.domain"
HELM_DEST="nexus.internal.domain"

echo "==> 1. Pulling Trivy Operator & Scanner Container Images..."
docker pull docker.io/aquasec/trivy-operator:0.22.0
docker pull docker.io/aquasec/trivy:0.52.0

echo "==> 2. Tagging Images for Internal Harbor..."
docker tag docker.io/aquasec/trivy-operator:0.22.0 ${HARBOR_DEST}/security/trivy-operator:0.22.0
docker tag docker.io/aquasec/trivy:0.52.0 ${HARBOR_DEST}/security/trivy:0.52.0

echo "==> 3. Mirroring Trivy Vulnerability OCI DB using Skopeo/Oras..."
skopeo copy docker://${HARBOR_SRC}/trivy-db:2 docker://${HARBOR_DEST}/mirror/aquasecurity/trivy-db:2
skopeo copy docker://${HARBOR_SRC}/trivy-java-db:1 docker://${HARBOR_DEST}/mirror/aquasecurity/trivy-java-db:1

echo "==> 4. Downloading Helm Chart for Nexus Upload..."
helm repo add aquasec https://aquasecurity.github.io/helm-charts
helm repo update
helm pull aquasec/trivy-operator --version 0.22.0 -d ./charts/

echo "==> Artifact preparation complete. Push artifacts across unidirectional diode."
```

---

## Phase 2: GitOps Configuration Setup

1. Clone your internal Git repository containing the ArgoCD application manifests.
2. Ensure `values-airgap.yaml` (from [04-baseline-architecture.md](file:///home/jakob/Code/security-scan/security/04-baseline-architecture.md)) is placed under `apps/trivy-operator/values-airgap.yaml`.
3. Ensure `trivy-operator-app.yaml` is committed under `apps/trivy-operator/application.yaml`.

---

## Phase 3: ArgoCD Deployment

Deploy the application into ArgoCD via `kubectl` or Ansible:

```bash
# Apply the ArgoCD Application manifest on the RKE2 Cluster
kubectl apply -f apps/trivy-operator/application.yaml -n argocd

# Force trigger ArgoCD sync (optional)
argocd app sync trivy-operator
```

---

## Phase 4: Verification & Operational Checks

### 1. Verify Operator & System Pod Health
```bash
# Verify namespace creation and pod readiness
kubectl get pods -n trivy-system -o wide

# Expected Output:
# NAME                                     READY   STATUS    RESTARTS   AGE
# trivy-operator-6987f6b9c9-x8j21          1/1     Running   0          2m
```

### 2. Verify Ephemeral Scan Pod Execution
```bash
# Watch scan jobs spawn and clean up automatically
kubectl get pods -n trivy-system -w | grep scan-vulnerabilityreport
```

### 3. Inspect Scan Reports (CRDs)
```bash
# List all generated Vulnerability Reports across the cluster
kubectl get vulnerabilityreports -A

# Inspect specific report details for a workload
kubectl get vulnerabilityreports -n default -o yaml

# Inspect Configuration Audits
kubectl get configauditreports -A
```

---

## Troubleshooting Guide for Air-Gapped Setup

| Symptom | Probable Cause | Resolution |
| :--- | :--- | :--- |
| Scan job fails with `ImagePullBackOff` | Ephemeral scan pod cannot pull `security/trivy:0.52.0` from Harbor. | Verify `imagePullSecrets` in `trivy-system` or check Harbor project public permissions. |
| Scan job times out or fails with `db download error` | `offlineScan: true` misconfigured or `dbRepository` endpoint inaccessible. | Confirm DNS resolution of `harbor.internal.domain` from within RKE2 pod network. Check OCI DB path in Harbor. |
| Etcd storage consumption growing | `scannerReportTTL` not set or reports not garbage collected. | Ensure `operator.scannerReportTTL: "24h"` is set in `values-airgap.yaml`. |
