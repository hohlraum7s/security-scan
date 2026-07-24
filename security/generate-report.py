#!/usr/bin/env python3
import json
import subprocess
import sys
from collections import defaultdict

def main():
    print("==========================================================================")
    print("        ACTIONABLE KUBERNETES VULNERABILITY REMEDIATION REPORT            ")
    print("==========================================================================")
    print()

    # Query all vulnerability reports in JSON format
    cmd = ["kubectl", "get", "vulnerabilityreports", "-A", "-o", "json"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
    except Exception as e:
        print(f"Error fetching vulnerability reports: {e}")
        sys.exit(1)

    items = data.get("items", [])
    if not items:
        print("No vulnerability reports found in the cluster.")
        return

    workload_summary = []
    cve_dedup = defaultdict(lambda: {
        "severity": "",
        "package": "",
        "installed": set(),
        "fixed": set(),
        "title": "",
        "workloads": set()
    })

    for item in items:
        metadata = item.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        name = metadata.get("name", "")
        report = item.get("report", {})
        artifact = report.get("artifact", {})
        image = f"{artifact.get('repository', '')}:{artifact.get('tag', '')}"
        
        vulnerabilities = report.get("vulnerabilities", [])
        if not vulnerabilities:
            continue

        critical_cves = [v for v in vulnerabilities if v.get("severity") == "CRITICAL"]
        high_cves = [v for v in vulnerabilities if v.get("severity") == "HIGH"]
        medium_cves = [v for v in vulnerabilities if v.get("severity") == "MEDIUM"]
        low_cves = [v for v in vulnerabilities if v.get("severity") == "LOW"]

        workload_summary.append({
            "namespace": namespace,
            "name": name,
            "image": image,
            "critical": len(critical_cves),
            "high": len(high_cves),
            "medium": len(medium_cves),
            "low": len(low_cves),
            "vulnerabilities": vulnerabilities
        })

        for v in vulnerabilities:
            cve_id = v.get("vulnerabilityID")
            if not cve_id:
                continue
            entry = cve_dedup[cve_id]
            entry["severity"] = v.get("severity", "UNKNOWN")
            entry["package"] = v.get("resource", "N/A")
            if v.get("installedVersion"):
                entry["installed"].add(v.get("installedVersion"))
            if v.get("fixedVersion"):
                entry["fixed"].add(v.get("fixedVersion"))
            entry["title"] = v.get("title", "")
            entry["workloads"].add(f"{namespace}/{name}")

    # 1. Deduplicated CVE Summary
    print("==========================================================================")
    print("                DEDUPLICATED UNIQUE CRITICAL & HIGH CVES                  ")
    print("==========================================================================")
    print(f"{'CVE ID':<18} {'SEVERITY':<10} {'PACKAGE':<20} {'FIXED VERSION':<20} {'AFFECTED WORKLOADS'}")
    print("-" * 90)

    sorted_cves = sorted(
        [k for k, v in cve_dedup.items() if v["severity"] in ["CRITICAL", "HIGH"]],
        key=lambda x: (cve_dedup[x]["severity"] != "CRITICAL", x)
    )

    for cve_id in sorted_cves:
        info = cve_dedup[cve_id]
        fixed_str = ", ".join(sorted(info["fixed"])) if info["fixed"] else "No fix"
        workload_count = len(info["workloads"])
        print(f"{cve_id:<18} {info['severity']:<10} {info['package']:<20} {fixed_str:<20} {workload_count} workload(s)")

    print("\nTotal Unique Critical CVEs:", sum(1 for k, v in cve_dedup.items() if v["severity"] == "CRITICAL"))
    print("Total Unique High CVEs:", sum(1 for k, v in cve_dedup.items() if v["severity"] == "HIGH"))

    print("\n" + "=" * 90)
    print("                 PER-WORKLOAD SECURITY BREAKDOWN TABLE                     ")
    print("=" * 90)
    print(f"{'NAMESPACE':<15} {'WORKLOAD':<40} {'CRITICAL':<10} {'HIGH':<8} {'MEDIUM':<8} {'FIXABLE'}")
    print("-" * 90)
    for ws in workload_summary:
        fixable_count = sum(1 for v in ws["vulnerabilities"] if v.get("fixedVersion"))
        print(f"{ws['namespace']:<15} {ws['name']:<40} {ws['critical']:<10} {ws['high']:<8} {ws['medium']:<8} {fixable_count}")

if __name__ == "__main__":
    main()
