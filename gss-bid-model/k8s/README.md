Kubernetes manifests for the GSS Bid Model service

Files:
- `deployment.yaml` - Deployment for the FastAPI app (replace image name)
- `service.yaml` - LoadBalancer service exposing port 80 -> 8000
- `hpa.yaml` - HorizontalPodAutoscaler (CPU-based)
- `secret-example.yaml` - Example secret for `FRED_API_KEY` (base64 placeholder)
- `ingress-example.yaml` - Example ingress rule (nginx)

How to deploy (example):

```bash
# Create secret (base64 or use kubectl create secret generic)
kubectl apply -f k8s/secret-example.yaml

# Replace image name in deployment.yaml or patch it after apply
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

Notes:
- Replace `REPLACE_WITH_IMAGE:latest` in `deployment.yaml` with a real image (from CI artifact or registry).
- Use `kubectl set image deployment/gss-bid-model gss-bid-model=<image>` to update image.
