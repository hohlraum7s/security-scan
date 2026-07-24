# 08 - Master Setup Requirements Checklist & Matrix

This document provides a comprehensive, consolidated checklist of all hardware, software, network, security, artifact, and operational requirements necessary to deploy and maintain the air-gapped RKE2 security scanner stack.

---

## 1. Hardware & Infrastructure Requirements

| ID | Requirement Category | Minimum Specification | Verification Command / Check |
| :--- | :--- | :--- | :--- |
| **HW-01** | **RKE2 Cluster Nodes** | Minimum 3 Control Plane / Worker nodes running Linux (RHEL 8/9, Rocky Linux, or Ubuntu 22.04 LTS). | `kubectl get nodes -o wide` |
| **HW-02** | **Node CPU Allocation** | At least 2 CPU cores free per node dedicated to Trivy Operator and ephemeral scan pods. | `kubectl describe nodes` |
| **HW-03** | **Node Memory Allocation**| At least 4 GB RAM free per node to support container scanning. | `free -h` |
| **HW-04** | **Node Storage Sizing** | 20 GB free disk space under `/var/lib/containerd` for local image caches. | `df -h /var/lib/containerd` |
| **HW-05** | **Storage Class** | Default K8s `StorageClass` for persistent volume claims (if report caching is enabled). | `kubectl get storageclass` |

---

## 2. Network & Air-Gap Requirements

| ID | Requirement Category | Minimum Specification | Verification Command / Check |
| :--- | :--- | :--- | :--- |
| **NET-01** | **Zero Internet Outbound** | Complete block of outbound egress to internet IP ranges from RKE2 cluster nodes. | `curl -m 5 https://google.com` (Must fail/timeout) |
| **NET-02** | **Internal DNS Resolution** | CoreDNS must resolve `harbor.internal.domain`, `nexus.internal.domain`, and `smtp.internal.domain`. | `nslookup harbor.internal.domain` inside cluster pod |
| **NET-03** | **Data Diode Sync** | Unidirectional data diode pipeline configured to push OCI database images to Harbor. | Verify OCI digest in Harbor UI |

---

## 3. Artifact & Registry Requirements

| ID | Requirement Category | Required Package / Image | Destination Store |
| :--- | :--- | :--- | :--- |
| **ART-01** | **Operator Image** | `aquasec/trivy-operator:0.22.0` | Harbor `security/trivy-operator:0.22.0` |
| **ART-02** | **Scanner Image** | `aquasec/trivy:0.52.0` | Harbor `security/trivy:0.52.0` |
| **ART-03** | **Trivy Vulnerability DB** | `ghcr.io/aquasecurity/trivy-db:2` (OCI Artifact) | Harbor `mirror/aquasecurity/trivy-db:2` |
| **ART-04** | **Trivy Java DB** | `ghcr.io/aquasecurity/trivy-java-db:1` (OCI Artifact) | Harbor `mirror/aquasecurity/trivy-java-db:1` |
| **ART-05** | **Helm Chart** | `trivy-operator-0.22.0.tgz` | Nexus Helm OCI Repository |

---

## 4. Security & Isolation Requirements

| ID | Requirement Category | Specification | Target Component |
| :--- | :--- | :--- | :--- |
| **SEC-01** | **Offline Mode Enforcement** | Helm value `trivy.offlineScan: true` must be explicitly set. | Helm Values Override |
| **SEC-02** | **Least Privilege RBAC** | Trivy Operator ServiceAccount limited to cluster-wide read access on workloads and write access on CRDs. | K8s ClusterRole & Binding |
| **SEC-03** | **Registry Credentials** | Harbor image pull secret (`harbor-registry-secret`) deployed to `trivy-system` and target namespaces. | K8s Secret |
| **SEC-04** | **Pod Security Standards** | Ephemeral scan pods must conform to RKE2 Restricted Pod Security Standards. | K8s PodSecurityContext |
| **SEC-05** | **Resource Limits** | Ephemeral scan pods restricted to `limits.cpu: 500m`, `limits.memory: 1Gi`. | Helm Values Override |

---

## 5. GitOps & Automation Requirements

| ID | Requirement Category | Specification | Tooling Used |
| :--- | :--- | :--- | :--- |
| **OPS-01** | **Declarative State** | 100% of security manifests, Helm values, and rules managed via internal Git repository. | Git / Gitea / GitLab |
| **OPS-02** | **GitOps Synchronization** | ArgoCD Application managing `trivy-operator` with automated pruning and self-healing. | ArgoCD Controller |
| **OPS-03** | **Ansible Automation** | Ansible playbooks for diode push verification, node secret distribution, and smoke testing. | Ansible Core 2.14+ |

---

## 6. Monitoring, Alerting & UI Requirements

| ID | Requirement Category | Specification | Component |
| :--- | :--- | :--- | :--- |
| **MON-01** | **Interactive Web UI** | Headlamp Kubernetes Web UI deployed with the Trivy Operator Headlamp plugin. | Headlamp UI |
| **MON-02** | **Metrics Exposer** | Helm value `trivyOperator.metricsFindings.enabled=true` enabled to expose `trivy_image_vulnerabilities`. | Trivy Operator |
| **MON-03** | **Grafana Dashboard** | `trivy-operator-dashboard` ConfigMap installed in `monitoring` namespace. | Grafana |
| **MON-04** | **Alertmanager Rules** | `PrometheusRule` manifest (`trivy-vulnerability-alerts`) deployed for Critical CVE routing. | Alertmanager |
| **MON-05** | **Report Garbage Collection** | `operator.scannerReportTTL: "24h"` set to prevent etcd bloat from old scan reports. | Trivy Operator |
