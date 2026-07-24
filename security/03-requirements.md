# 03 - Requirements Specification

This document details the functional, non-functional, security, and operational requirements for the air-gapped security scanner stack.

---

## 1. Functional Requirements (FR)

| ID | Requirement | Description | Target Component |
| :--- | :--- | :--- | :--- |
| **FR-01** | Continuous Image Scanning | Automatically discover and scan all running container images across all active Kubernetes namespaces upon pod creation or updates. | Trivy Operator |
| **FR-02** | Offline Vulnerability Database | Perform image scanning against locally hosted CVE database bundles stored as OCI artifacts in Harbor without internet lookup. | Trivy Standalone Engine |
| **FR-03** | Kubernetes Configuration Audit | Scan cluster manifests, workloads, and pod security specs against Pod Security Standards (PSS) and Security Context best practices. | Trivy ConfigAudit Engine |
| **FR-04** | Exposed Secret Scanning | Scan container images and config maps for exposed API keys, tokens, and private keys. | Trivy Secret Engine |
| **FR-05** | RBAC Role Risk Assessment | Analyze cluster roles and service accounts for over-privileged permissions or excessive cluster-admin bindings. | Trivy RBAC Assessor |
| **FR-06** | Kubernetes Native Reporting | Expose all scan results as standard K8s Custom Resource Definitions (CRDs) queryable via `kubectl`. | K8s CRD Controller |

---

## 2. Non-Functional Requirements (NFR)

| ID | Requirement | Metric / Target |
| :--- | :--- | :--- |
| **NFR-01** | Zero Outbound Network Access | `0` outbound calls to external internet domains during scan execution. |
| **NFR-02** | Low Cluster Resource Impact | Operator RAM limit ≤ 500Mi; Scan Job ephemeral memory ≤ 1Gi. Scan jobs must use `Nice` priority. |
| **NFR-03** | Scan Job Timeout Safeguard | Individual image scan jobs must time out after 15 minutes to prevent hung pods. |
| **NFR-04** | Declarative GitOps State | 100% of security scanner resources managed via GitOps with automatic drift correction in ArgoCD. |
| **NFR-05** | Air-Gap Data Staleness | Vulnerability database staleness governed by diode sync schedule (target ≤ 24-48 hours old). |

---

## 3. Security Requirements (SEC)

* **SEC-01: Service Account Least Privilege**: The Trivy Operator ServiceAccount must be scoped with minimal required ClusterRole permissions to read workloads and write security CRDs.
* **SEC-02: Secret Isolation**: Registry credentials used to pull images from Harbor must be stored in secure K8s Secrets, referenced by `imagePullSecrets`.
* **SEC-03: Offline Cache Integrity**: Vulnerability DB OCI artifacts pushed through the diode must be validated against checksums before ingestion into Harbor.

---

## 4. Operational Requirements (OP)

* **OP-01: Automated Report Retention**: Scan reports older than 24-48 hours must be automatically garbage-collected (`scannerReportTTL: "24h"`) to prevent etcd bloated state.
* **OP-02: Health Monitoring**: Operator readiness and liveness probes must integrate with Kubernetes health check endpoints.
