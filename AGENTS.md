# AGENTS.md - Developer & Agent Guidance

This document provides context, conventions, guidelines, and repository structure for AI agents and developers working on this air-gapped RKE2 security scanner repository.

---

## 1. Project Mission & Context

This repository contains the architecture, planning, configuration manifests, and deployment automation for an **air-gapped security scanning stack** targeting a standalone **RKE2 Kubernetes cluster**.

Key System Constraints:
* **Zero Outbound Internet Access**: Applications inside the cluster have no direct internet egress.
* **Diode Ingestion**: External artifacts (container images, Helm charts, CVE database bundles) pass through a one-way unidirectional data diode into internal **Harbor** and **Nexus** registries.
* **Tooling Standards**: Helm v3, ArgoCD (GitOps), Ansible, Trivy Operator, Headlamp UI, Grafana, and Prometheus Alertmanager.

---

## 2. Directory & Repository Map

```text
/home/jakob/Code/security-scan/
├── AGENTS.md                              # This guidance file for agents & developers
├── .gitignore                             # Git ignore specifications
├── security-dashboard-setup.yaml          # ServiceMonitor & Grafana Dashboard ConfigMap
├── security/
│   ├── README.md                          # Master project plan index & navigation
│   ├── 01-directives.md                   # Directives & zero-outbound governance
│   ├── 02-prerequisites.md                # System prerequisites (RKE2, Harbor, Nexus, Diode)
│   ├── 03-requirements.md                # Functional & non-functional requirements
│   ├── 04-baseline-architecture.md        # Technical baseline (Helm & ArgoCD specs)
│   ├── 05-deployment-guide.md             # Execution playbook & diode sync script
│   ├── 06-admin-monitoring-plan.md        # Multi-tiered admin monitoring framework (Headlamp/Grafana/Alertmanager)
│   ├── 07-prometheus-alertmanager-config.md # Prometheus & Alertmanager setup guide
│   ├── 08-master-requirements-checklist.md # Consolidated master requirements matrix
│   ├── 09-argocd-helm-deployment-guide.md # ArgoCD Helm deployment guide
│   ├── values-prometheus.yaml             # Production Helm values for Prometheus & Alertmanager
│   ├── trivy-prometheus-rules.yaml        # PrometheusRule CRD for security alerts
│   ├── cve-api-deployment.yaml            # In-cluster Critical CVE API server deployment
│   ├── generate-report.py                 # CLI report generator for deduplicated CVEs
│   └── cve-server.py                      # Standalone Python CVE API server
```

---

## 3. Formatting & Behavioral Rules for Agents

When creating, updating, or editing files in this repository, follow these rules:

1. **No Emojis**: Do not use emojis in markdown documentation, code comments, or tool outputs.
2. **Declarative GitOps First**: All Kubernetes manifests must be declarative. Avoid imperative `kubectl create` in production manifests; store resources as version-controlled YAML.
3. **Air-Gap Compliance**:
   - Ensure all container images reference internal registries (`harbor.internal.domain`).
   - Enforce `trivy.offlineScan: true` in Helm configurations.
   - Point OCI vulnerability database repositories to `harbor.internal.domain/mirror/aquasecurity/trivy-db`.
4. **Markdown Formatting**:
   - Use GitHub-flavored Markdown.
   - Include relative or absolute `file://` links for file references.
   - Maintain concise tables and clean headers.

---

## 4. Verification & Testing Playbook

When making changes to manifests or scripts, verify them using the local test environment:

```bash
# Check Trivy Operator deployment state
kubectl get pods -n trivy-system

# Verify generated vulnerability reports
kubectl get vulnerabilityreports -A -o wide

# Execute the CLI report generator
python3 security/generate-report.py

# Validate YAML syntax on Kubernetes manifests
kubectl apply --dry-run=client -f security-dashboard-setup.yaml
```
