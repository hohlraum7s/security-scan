# Trivy Operator & Security Scanner Module

This directory contains the declarative Kubernetes manifests, Helm values, and reporting scripts for running the Aqua Trivy Operator in an air-gapped environment.

---

## Directory Structure

```text
trivy/
├── README.md                            # Module documentation
├── manifests/
│   ├── trivy-namespace.yaml             # Declarative trivy-system namespace
│   ├── values-trivy-minikube-airgap.yaml # Helm values for offline scanning testing
│   ├── trivy-prometheus-rules.yaml      # PrometheusRule CRD for security alerts
│   ├── cve-api-deployment.yaml          # In-cluster Critical CVE REST API
│   └── security-dashboard-setup.yaml    # ServiceMonitor & Grafana Dashboard ConfigMap
└── scripts/
    ├── cve-server.py                    # Standalone Python CVE API server
    └── generate-report.py               # CLI report generator for deduplicated CVEs
```

---

## Quickstart (Minikube / Testing)

### 1. Create Namespace & Deploy Trivy Operator
```bash
kubectl apply -f trivy/manifests/trivy-namespace.yaml
helm upgrade --install trivy-operator aquasec/trivy-operator \
  --namespace trivy-system \
  -f trivy/manifests/values-trivy-minikube-airgap.yaml
```

### 2. Apply ServiceMonitor & Alerting Rules
```bash
kubectl apply -f trivy/manifests/security-dashboard-setup.yaml
kubectl apply -f trivy/manifests/trivy-prometheus-rules.yaml -n monitoring
```

### 3. Generate Report CLI
```bash
python3 trivy/scripts/generate-report.py
```
