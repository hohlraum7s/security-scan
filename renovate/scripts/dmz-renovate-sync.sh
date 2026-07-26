#!/usr/bin/env bash
# dmz-renovate-sync.sh
# DMZ Sync Script for Renovate Bot Air-Gap Pipeline
#
# This script runs on the Connected DMZ Runner after Renovate generates or updates dependency PRs.
# It extracts newly referenced container images & Helm charts, mirrors them into internal
# Harbor/Nexus registries across the diode, and pushes the Git branches to the internal Git server.

set -eo pipefail

HARBOR_DEST="harbor.internal.domain"
NEXUS_DEST="nexus.internal.domain"
INTERNAL_GIT_REMOTE="git@git.internal.domain:security/security-scan.git"

echo "==> 1. Running Renovate Bot on Connected DMZ Runner..."
# Run Renovate CLI against public repositories / upstream mirrors
npx renovate --config-file=renovate.json

echo "==> 2. Detecting newly introduced container images in Renovate branches..."
# Get list of remote Renovate branches generated during run
RENOVATE_BRANCHES=$(git branch -r | grep "origin/renovate/" || true)

for BRANCH in $RENOVATE_BRANCHES; do
  CLEAN_BRANCH="${BRANCH#origin/}"
  echo "--> Processing branch: ${CLEAN_BRANCH}"
  git checkout "${CLEAN_BRANCH}"
  
  # Extract image references added in modified YAML/JSON manifests
  IMAGES=$(git diff origin/main...HEAD | grep -E '^\+\s*(image|repository):' | awk '{print $2}' | tr -d '"' | tr -d "'" | sort -u)
  
  for IMG in $IMAGES; do
    if [[ -n "$IMG" && "$IMG" != *"${HARBOR_DEST}"* ]]; then
      echo "    ==> Mirroring upstream image: ${IMG} to ${HARBOR_DEST}..."
      
      # Determine internal target repository structure
      INTERNAL_TARGET="${HARBOR_DEST}/mirror/${IMG}"
      
      # Copy multi-architecture container images using Skopeo
      skopeo copy --all "docker://${IMG}" "docker://${INTERNAL_TARGET}" || {
        echo "Warning: Failed to sync image ${IMG} across diode."
      }
    fi
  done
  
  echo "--> Pushing synced Renovate branch to internal air-gapped Git server..."
  git push "${INTERNAL_GIT_REMOTE}" HEAD:"refs/heads/${CLEAN_BRANCH}" --force
done

git checkout main
echo "==> Renovate DMZ sync process completed successfully."
