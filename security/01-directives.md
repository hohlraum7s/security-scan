# 01 - Project Directives & Governance

## Executive Vision

The objective of this initiative is to establish a secure, resilient, and continuous security scanning infrastructure tailored for a standalone RKE2 Kubernetes cluster operating in a **semi-air-gapped environment**.

Applications running inside the Kubernetes cluster will **never have direct internet access**. All external software, vulnerability definitions, and system dependencies must strictly pass through an automated one-way **unidirectional data diode** feeding internal artifact repositories (**Harbor** and **Nexus**).

---

## Mandatory Directives & Security Rules

### 1. Absolute Zero-Outbound Network Rule
* No workload or system pod inside the RKE2 cluster is allowed to open outbound internet connections (HTTP/HTTPS/DNS).
* All security scanning tools must operate natively in offline mode (`offlineScan: true`).
* Any dependency (e.g. CVE databases, Java package databases, container images, Helm charts) must be resolved locally via internal endpoints (`harbor.internal.domain`, `nexus.internal.domain`).

### 2. Mandatory Tech Stack Alignment
The security solution must fit seamlessly into the organization's pre-approved operational stack:
* **Orchestration Platform**: Standalone RKE2 (Rancher Kubernetes Engine 2).
* **GitOps Engine**: ArgoCD (all deployments must be declarative and managed via Git).
* **Package Management**: Helm v3 (charts stored in internal OCI / Nexus repos).
* **Infrastructure Automation**: Ansible (playbooks for node provisioning, diode pipeline triggers, secret injection).

### 3. Native Kubernetes Integration
* Security reports must be generated as standard Kubernetes Custom Resource Definitions (CRDs) inside the cluster (`VulnerabilityReport`, `ConfigAuditReport`, `RbacAssessmentReport`).
* Security findings must be queryable via standard Kubernetes API channels (`kubectl`, RBAC-controlled roles, ArgoCD UI).

### 4. Zero Manual Maintenance on Cluster Nodes
* Scanning engines must be deployed as Kubernetes operators, avoiding node-level sidecars or static systemd agents where possible.
* All configuration changes must be driven by Git repositories synced via ArgoCD.

---

## Scope Boundaries

### In Scope
- Deployment of **Trivy Operator** via Helm & ArgoCD.
- Continuous vulnerability scanning of all active container images across all namespaces.
- Kubernetes configuration auditing (Pod Security Standards, container security context checks).
- RBAC role risk assessment and secret exposure detection inside container images.
- Air-gapped CVE database update pipeline (via OCI artifact push through data diode into Harbor).

### Out of Scope (Phase 1 Baseline)
- Real-time kernel eBPF runtime threat blocking (planned for Phase 2 - Falco evaluation).
- Dynamic Web Application Security Testing (DAST) against live endpoints.
- Third-party SaaS security reporting integration.
