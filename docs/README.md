# Air-Gapped Security Scanner Project Plan

Welcome to the Air-Gapped Security Scanner project repository for the RKE2 Kubernetes platform. This directory contains the complete architectural directives, prerequisites, technical requirements, baseline configuration, deployment procedures, administrator monitoring frameworks, Prometheus alerting configurations, master requirement checklists, and ArgoCD Helm deployment guides for establishing an automated, offline container security scanner stack.

---

## Plan Structure & Navigation

| Document | Title & Description |
| :--- | :--- |
| **[01-directives.md](file:///home/jakob/Code/security-scan/docs/01-directives.md)** | **Project Directives**: High-level vision, scope boundaries, architectural principles, and air-gap design rules. |
| **[02-prerequisites.md](file:///home/jakob/Code/security-scan/docs/02-prerequisites.md)** | **Prerequisites**: Infrastructure requirements, RKE2 cluster baseline, Harbor/Nexus setup, and diode pipeline specs. |
| **[03-requirements.md](file:///home/jakob/Code/security-scan/docs/03-requirements.md)** | **Requirements Specification**: Functional, non-functional, security, and operational criteria. |
| **[04-baseline-architecture.md](file:///home/jakob/Code/security-scan/docs/04-baseline-architecture.md)** | **Baseline Architecture**: System design, component interaction, OCI DB mirroring, Helm config, and ArgoCD application specs. |
| **[05-deployment-guide.md](file:///home/jakob/Code/security-scan/docs/05-deployment-guide.md)** | **Deployment Guide**: Execution playbook using Ansible, Helm, and ArgoCD to deploy and verify the scanner. |
| **[06-admin-monitoring-plan.md](file:///home/jakob/Code/security-scan/docs/06-admin-monitoring-plan.md)** | **Admin Monitoring Architecture**: Multi-tiered monitoring framework featuring Headlamp UI, Grafana, Alertmanager, and SIEM logging. |
| **[07-prometheus-alertmanager-config.md](file:///home/jakob/Code/security-scan/docs/07-prometheus-alertmanager-config.md)** | **Prometheus & Alertmanager Config**: Complete setup guide and production `values-prometheus.yaml` for automated security alerts. |
| **[08-master-requirements-checklist.md](file:///home/jakob/Code/security-scan/docs/08-master-requirements-checklist.md)** | **Master Requirements Checklist**: Consolidated hardware, software, network, artifact, security, and monitoring requirements matrix. |
| **[09-argocd-helm-deployment-guide.md](file:///home/jakob/Code/security-scan/docs/09-argocd-helm-deployment-guide.md)** | **ArgoCD Helm Deployment Guide**: Detailed step-by-step guide for deploying Helm charts declaratively via ArgoCD in air-gapped environments. |

---

## Technology Stack Overview

- **Target Platform**: RKE2 (Rancher Kubernetes Engine 2 - Standalone Cluster)
- **Security Scanner Engine**: [Trivy Operator](https://github.com/aquasecurity/trivy-operator)
- **Interactive UI**: Headlamp (CNCF Kubernetes Web UI + Trivy Plugin)
- **Dashboards & Alerting**: Grafana & Prometheus Alertmanager
- **Deployment & Lifecycle**: Argo CD (GitOps) & Helm
- **Automation & Node Setup**: Ansible
- **Artifact & Image Storage**: Harbor (Container Images & OCI Trivy DBs) & Nexus (Helm Charts)
- **Air-Gap Data Transfer**: Unidirectional Data Diode (One-way sync into internal Harbor/Nexus)

---

## Quick Reference Architecture

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 Unidirectional Data Diode               │
                  └────────────────────────────┬────────────────────────────┘
                                               │ Ingress Sync
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Air-Gapped Environment                                                      │
│                                                                             │
│  ┌─────────────────────────┐               ┌─────────────────────────────┐  │
│  │ Harbor (OCI Registry)   │               │ Nexus Repository            │  │
│  │ • Operator Images       │               │ • Helm Charts               │  │
│  │ • Trivy DB (OCI)        │               │ • Binary Dependencies       │  │
│  └────────────┬────────────┘               └──────────────┬──────────────┘  │
│               │ Pull                                      │ Chart Pull      │
│               └──────────────────────┬────────────────────┘                 │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │ RKE2 Cluster                                                          │  │
│  │                                                                       │  │
│  │   ┌───────────────────────────┐      ┌─────────────────────────────┐  │  │
│  │   │ ArgoCD Controller         ├─────►│ Trivy Operator              │  │  │
│  │   └───────────────────────────┘      │ • Workload Scanner          │  │  │
│  │                                      │ • Config & Secret Audit     │  │  │
│  │                                      │ • RBAC Assessor             │  │  │
│  │                                      └──────────────┬──────────────┘  │  │
│  │                                                     │ Generates       │  │
│  │                                      ┌──────────────▼──────────────┐  │  │
│  │                                      │ K8s Reports (Vulnerability, │  │  │
│  │                                      │ ConfigAudit CRDs)           │  │  │
│  │                                      └──────────────┬──────────────┘  │  │
│  │                                                     │ Exposes         │  │
│  │  ┌──────────────────────────────────────────────────┴──────────────┐  │  │
│  │  │ Admin Visibility Layer                                          │  │  │
│  │  │ • Headlamp UI (Interactive Pod/CVE Tab)                         │  │  │
│  │  │ • Grafana (Posture Trends & Scanner Health)                     │  │  │
│  │  │ • Alertmanager (Proactive Push Notifications)                   │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```
