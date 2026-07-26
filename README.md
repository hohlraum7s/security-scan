# Air-Gapped RKE2 Security Scanning Stack

An architecture, planning, and deployment repository for establishing an **automated, continuous, air-gapped security scanning infrastructure** on standalone **RKE2 (Rancher Kubernetes Engine 2)** clusters.

---

## 🎯 Overview & Architecture

This security stack operates natively inside an air-gapped environment with **zero outbound internet access**. External artifacts (container images, Helm charts, and Trivy vulnerability database bundles) pass through a one-way unidirectional data diode into internal artifact stores (**Harbor** and **Nexus**).

```text
  [ Outside World ]                      [ Air-Gapped Environment ]
┌──────────────────┐               ┌────────────────────────────────────┐
│ Upstream Sources ├───(Diode)────►│ Internal Repositories              │
│ • Docker Hub     │               │ • Harbor (Container Images & DBs)  │
│ • trivy-db (OCI) │               │ • Nexus (Helm Charts)              │
└──────────────────┘               └─────────────────┬──────────────────┘
                                                     │ Pull
                                                     ▼
                                   ┌────────────────────────────────────┐
                                   │ RKE2 Kubernetes Cluster            │
                                   │                                    │
                                   │  ┌──────────────────────────────┐  │
                                   │  │ Argo CD (GitOps Controller)  │  │
                                   │  └──────────────┬───────────────┘  │
                                   │                 │ Deploy           │
                                   │  ┌──────────────▼───────────────┐  │
                                   │  │ Trivy Operator               │  │
                                   │  │ • Workload & Image Scanner   │  │
                                   │  │ • Config Audit & Secrets     │  │
                                   │  └──────────────┬───────────────┘  │
                                   │                 │ Reports          │
                                   │  ┌──────────────▼───────────────┐  │
                                   │  │ Kubernetes CRDs              │  │
                                   │  └──────────────┬───────────────┘  │
                                   │                 │ Exposes          │
                                   │  ┌──────────────▼───────────────┐  │
                                   │  │ Admin Visibility Layer       │  │
                                   │  │ • Headlamp UI (Pod Security) │  │
                                   │  │ • Grafana (Posture Trends)   │  │
                                   │  │ • Alertmanager (Push Alerts) │  │
                                   │  └──────────────────────────────┘  │
                                   └────────────────────────────────────┘
```

---

## 📁 Repository Structure

```text
.
├── README.md                              # Main repository overview and quick start
├── AGENTS.md                              # Context and guidelines for developers & AI subagents
├── trivy/                                 # Trivy Operator & Scanner module
│   ├── README.md                          # Trivy quickstart & documentation
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
    ├── README.md                          # Master project plan index & document sitemap
    ├── 01-directives.md                   # Business goals, scope, and zero-outbound governance
    ├── 02-prerequisites.md                # Infrastructure, RKE2, Harbor, Nexus & Diode specs
    ├── 03-requirements.md                # Functional, non-functional, and security requirements
    ├── 04-baseline-architecture.md        # Helm values, ArgoCD Application, and CRD specs
    ├── 05-deployment-guide.md             # Execution playbook and diode mirror script
    ├── 06-admin-monitoring-plan.md        # Multi-tiered admin monitoring framework
    ├── 07-prometheus-alertmanager-config.md # Prometheus & Alertmanager configuration guide
    ├── 08-master-requirements-checklist.md # Master requirements checklist and matrix
    └── 09-argocd-helm-deployment-guide.md # ArgoCD Helm deployment guide
```

---

## 🚀 Quick Start Guide

### 1. Local Verification (Minikube / Test Cluster)

Deploy Trivy Operator locally via Helm:

```bash
# Add Aqua Security Helm repository
helm repo add aquasec https://aquasecurity.github.io/helm-charts
helm repo update

# Install Trivy Operator in trivy-system namespace
helm install trivy-operator aquasec/trivy-operator \
  --namespace trivy-system \
  --create-namespace \
  --set trivyOperator.metricsFindings.enabled=true
```

### 2. Generate Deduplicated Vulnerability Report

Run the included report generator script to view a deduplicated summary of all Critical and High vulnerabilities:

```bash
python3 security/generate-report.py
```

### 3. Deploy Security Dashboard & Prometheus Rules

```bash
# Deploy Grafana Dashboard & ServiceMonitor
kubectl apply -f security-dashboard-setup.yaml

# Deploy Prometheus Alerting Rules
kubectl apply -f security/trivy-prometheus-rules.yaml -n monitoring
```

---

## 📄 Documentation Sitemap

* **[Directives & Governance](file:///home/jakob/Code/security-scan/docs/01-directives.md)**: Zero-outbound internet rules and architecture principles.
* **[Prerequisites Specification](file:///home/jakob/Code/security-scan/docs/02-prerequisites.md)**: Infrastructure, Harbor, Nexus, and data diode pipeline requirements.
* **[Baseline Architecture](file:///home/jakob/Code/security-scan/docs/04-baseline-architecture.md)**: Offline Helm values and ArgoCD manifest templates.
* **[Deployment Guide](file:///home/jakob/Code/security-scan/docs/05-deployment-guide.md)**: Execution playbook for diode sync and verification.
* **[Admin Monitoring Plan](file:///home/jakob/Code/security-scan/docs/06-admin-monitoring-plan.md)**: Multi-tiered admin monitoring featuring Headlamp, Grafana, and Alertmanager.
* **[Prometheus & Alertmanager Config](file:///home/jakob/Code/security-scan/docs/07-prometheus-alertmanager-config.md)**: Setup guide for automated alert routing.
* **[Master Requirements Matrix](file:///home/jakob/Code/security-scan/docs/08-master-requirements-checklist.md)**: Master setup requirements checklist.
* **[ArgoCD Helm Deployment Guide](file:///home/jakob/Code/security-scan/docs/09-argocd-helm-deployment-guide.md)**: Step-by-step ArgoCD GitOps deployment guide.

---

## 🤖 Developer & Agent Guidance

Refer to **[AGENTS.md](file:///home/jakob/Code/security-scan/AGENTS.md)** for developer conventions, formatting guidelines, and test playbooks when extending or modifying this repository.
