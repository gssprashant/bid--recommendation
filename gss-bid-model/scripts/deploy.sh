#!/usr/bin/env bash
set -euo pipefail

IMAGE=${1:-REPLACE_WITH_IMAGE:latest}

echo "Using image: $IMAGE"

# Patch deployment image then apply all manifests
kubectl -n default create secret generic gss-bid-secrets --from-literal=FRED_API_KEY=$FRED_API_KEY --dry-run=client -o yaml | kubectl apply -f - || true

kubectl apply -f k8s/secret-example.yaml || true

# Apply deployment and service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml || true

# Patch the image if user provided one
kubectl set image deployment/gss-bid-model gss-bid-model=${IMAGE} --record || true

echo "Deployed (or updated) gss-bid-model to the cluster."
