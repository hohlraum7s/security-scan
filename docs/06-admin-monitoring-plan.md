# 06 - Administrator Monitoring & Visibility Architecture

This document outlines the multi-tiered monitoring, dashboarding, and alerting framework for cluster administrators operating an air-gapped RKE2 security scanner.

---

## 1. Multi-Tiered Monitoring Overview

To ensure administrators have reliable, real-time, and historical visibility into cluster security, the monitoring architecture is divided into four complementary layers:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ RKE2 Air-Gapped Administrator Monitoring Framework                               │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Tier 1: Interactive Day-to-Day UI (Headlamp + Trivy Plugin)                       │
│   • Visual inspection of workloads, pods, and security reports                   │
│   • Actionable CVE tables per pod with direct fix versions                       │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Tier 2: Executive & Operational Dashboards (Grafana + Prometheus)               │
│   • Cluster-wide posture trends, unique CVE counts, and namespace heatmaps        │
│   • Scanner health metrics (queue depth, scan job duration, failure rates)       │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Tier 3: Proactive Push Alerting (Alertmanager)                                   │
│   • Real-time notifications for Critical CVEs and root container executions      │
│   • Scheduled daily/weekly executive summary digests                             │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Tier 4: Centralized SIEM & Audit Forwarding (Vector / Fluent Bit / Syslog)       │
│   • Immutable audit logs of all security scan findings for compliance reporting  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier 1: Interactive Cluster Management via Headlamp

**Headlamp** serves as the primary interactive Web UI for cluster administrators and application developers.

### Headlamp Trivy Plugin Integration
* **Installation**: Deployed as an in-cluster web UI or Headlamp plugin.
* **UI Experience**:
  * Adds a native **Security Tab** to every Pod, Deployment, StatefulSet, and Namespace view.
  * Allows admins to inspect full CVE details (`CVE ID`, `Package`, `Installed Version`, `Fixed Version`, `Description`) with zero CLI commands required.
  * Displays Pod Security Standard (PSS) compliance audit scores alongside workload manifests.

---

## 3. Tier 2: Operational & Health Dashboards (Grafana + Prometheus)

Grafana provides high-level metric aggregation, SLA tracking, and scanner operational monitoring.

### A. Security Posture Dashboard
* **Unique Critical CVE Count**: Deduplicated count of Critical vulnerabilities active across the cluster.
* **Workload Vulnerability Heatmap**: Namespace-by-namespace breakdown of security health.
* **Remediation SLA Tracking**: Tracks the age of unresolved Critical/High vulnerabilities.

### B. Trivy Operator Health Dashboard
Admins must monitor the scanner itself to ensure air-gapped database syncs and scan jobs operate reliably:
* `trivy_operator_scan_jobs_active`: Number of concurrent scan pods running.
* `trivy_operator_scan_job_duration_seconds`: Identifies slow or hung image scans.
* `trivy_operator_reconcile_errors_total`: Alerts if Trivy Operator fails to access Harbor or parse manifests.

---

## 4. Tier 3: Proactive Push Alerting Strategy

Admins should be notified automatically without needing to monitor dashboards 24/7.

| Alert Name | Condition | Severity | Notification Channel |
| :--- | :--- | :--- | :--- |
| `TrivyCriticalCVEFound` | `trivy_image_vulnerabilities{severity="Critical"} > 0` for 5m | Critical | Immediate Webhook / Email / Teams |
| `TrivyScannerFailure` | `rate(trivy_operator_reconcile_errors_total[15m]) > 0` | Warning | DevOps Alert Channel |
| `TrivyAirGapDBCacheStale` | Harbor trivy-db tag age > 72 hours | Warning | Diode Sync Automation Alert |

---

## 5. Tier 4: SIEM & Audit Log Export

For long-term compliance and auditability:
* **Log Shipper**: Deploy **Vector** or **Fluent Bit** to read Kubernetes event streams and `VulnerabilityReport` CRD state changes.
* **Destination**: Stream structured JSON audit logs across internal syslog/Elasticsearch/Splunk servers.
