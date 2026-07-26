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
├── AGENTS.md                              # Guidance file for agents & developers
├── README.md                              # Master project overview
├── trivy/                                 # Trivy Operator & Scanner module
│   ├── README.md                          # Module quickstart & overview
│   ├── manifests/                         # Declarative K8s manifests & Helm values
│   │   ├── trivy-namespace.yaml
│   │   ├── values-trivy-minikube-airgap.yaml
│   │   ├── trivy-prometheus-rules.yaml
│   │   ├── cve-api-deployment.yaml
│   │   └── security-dashboard-setup.yaml
│   └── scripts/                           # Reporting & REST API scripts
│       ├── cve-server.py
│       └── generate-report.py
├── renovate/                              # Renovate Bot air-gapped sync module
│   ├── README.md                          # Air-gap sync documentation
│   ├── config/                            # Renovate configuration file
│   │   └── renovate.json
│   └── scripts/                           # DMZ diode sync script
│       └── dmz-renovate-sync.sh
├── prometheus/                            # Prometheus & Alertmanager configs
│   └── values-prometheus.yaml
└── docs/                                  # Architecture & planning documentation
    ├── README.md                          # Master documentation index
    ├── 01-directives.md
    ├── 02-prerequisites.md
    ├── 03-requirements.md
    ├── 04-baseline-architecture.md
    ├── 05-deployment-guide.md
    ├── 06-admin-monitoring-plan.md
    ├── 07-prometheus-alertmanager-config.md
    ├── 08-master-requirements-checklist.md
    └── 09-argocd-helm-deployment-guide.md
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
python3 trivy/scripts/generate-report.py

# Validate YAML syntax on Kubernetes manifests
kubectl apply --dry-run=client -f trivy/manifests/security-dashboard-setup.yaml
```
