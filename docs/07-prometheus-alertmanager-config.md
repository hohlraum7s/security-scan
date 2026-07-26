# 07 - Prometheus & Alertmanager Configuration Guide

This guide details how to configure **Prometheus** and **Alertmanager** declaratively via Helm and ArgoCD to automatically detect Trivy security findings and trigger alerts.

---

## 1. Declarative Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Prometheus & Alertmanager Security Flow                                          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Trivy Operator Scraped by Prometheus via ServiceMonitor                       │
│    • Target: http://trivy-operator.trivy-system.svc:8080/metrics                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. Prometheus Evaluates PrometheusRules                                          │
│    • Rule: TrivyCriticalVulnerabilityDetected (expr: sum(severity="Critical")>0) │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. Prometheus Sends Active Alert Payload to Alertmanager                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 4. Alertmanager Deduplicates, Groups, and Routes to Receivers                    │
│    • Critical Alerts ──► Mattermost / ChatOps Webhook                            │
│    • Daily Summaries ──► Security Email (secops@internal.domain)                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Configuration Step-by-Step

### Step 1: Deploy / Update Helm Values (`values-prometheus.yaml`)
Pass the updated Helm values file [`security/values-prometheus.yaml`](file:///home/jakob/Code/security-scan/security/values-prometheus.yaml) to your `kube-prometheus-stack` chart release:

```bash
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f security/values-prometheus.yaml
```

### Step 2: Apply the Security PrometheusRules
Apply the alert definitions from [`security/trivy-prometheus-rules.yaml`](file:///home/jakob/Code/security-scan/security/trivy-prometheus-rules.yaml):

```bash
kubectl apply -f security/trivy-prometheus-rules.yaml -n monitoring
```

### Step 3: Verify Alertmanager Configuration
Confirm that Alertmanager successfully loaded the routing rules:

```bash
# Check if Alertmanager pod is healthy
kubectl get pods -n monitoring -l app.kubernetes.io/name=alertmanager

# Inspect the loaded Alertmanager configuration
kubectl exec -n monitoring alertmanager-kube-prometheus-stack-alertmanager-0 -c alertmanager -- amtool config show
```

---

## 3. How to Test Alerts

You can test that Alertmanager properly routes notifications by deploying a test workload with a known Critical CVE:

```bash
# Deploy a vulnerable image
kubectl create deployment test-vulnerable-app --image=nginx:1.16 -n default

# Wait for Trivy Operator to generate reports
kubectl get vulnerabilityreports -n default

# Verify firing alerts in Prometheus
kubectl exec -n monitoring prometheus-kube-prometheus-stack-prometheus-0 -c prometheus -- curl -s http://localhost:9090/api/v1/alerts | grep -i TrivyCriticalVulnerabilityDetected
```
