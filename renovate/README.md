# Renovate Bot Air-Gap Integration Module

This directory contains the configuration and synchronization automation for running Renovate Bot alongside an air-gapped Kubernetes environment.

---

## Directory Structure

```text
renovate/
├── README.md                            # Module documentation
├── config/
│   └── renovate.json                    # Renovate Bot configuration with post-upgrade hooks
└── scripts/
    └── dmz-renovate-sync.sh             # DMZ runner sync script for diode mirroring
```

---

## Workflow Overview

1. **DMZ Runner**: Renovate runs on a connected staging host outside the air-gap and inspects upstream public container/helm registries.
2. **Post-Upgrade Sync**: When Renovate opens or updates a PR, [dmz-renovate-sync.sh](file:///home/jakob/Code/security-scan/renovate/scripts/dmz-renovate-sync.sh) extracts newly introduced container image tags and uses `skopeo` to push them across the diode into internal Harbor (`harbor.internal.domain`).
3. **Internal Git Mirroring**: The PR branch is pushed to the internal air-gapped Git server where cluster administrators can safely review and merge it.

---

## Usage

Run the DMZ sync script on the connected staging host:
```bash
./renovate/scripts/dmz-renovate-sync.sh
```
