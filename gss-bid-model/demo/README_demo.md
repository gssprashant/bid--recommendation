Demo: minimal setup for quick presentations

This folder contains a simplified, minimal set of files you can use to demo the model quickly.

Files:
- `Dockerfile` - single-stage image suitable for demos (no wheel caching)
- `k8s/simple-deployment.yaml` - minimal Deployment + Service (replace image tag)
- `run_local.ps1` - quick PowerShell helper to build and run locally

Quick local demo (PowerShell):

```powershell
# Build image
docker build -t gss-bid-demo:latest -f demo/Dockerfile .

# Run container (exposes 8000)
docker run --rm -p 8000:8000 --name gss-bid-demo gss-bid-demo:latest

# Check health
Invoke-RestMethod -Uri http://localhost:8000/health
```

Simple k8s deploy (for kind or any cluster):

```bash
# replace image name in demo/k8s/simple-deployment.yaml or use kubectl set image
kubectl apply -f demo/k8s/simple-deployment.yaml
kubectl apply -f demo/k8s/simple-service.yaml
```

Notes:
- This demo image is intentionally minimal and intended for slides/demos. Use the main `Dockerfile` and k8s manifests for production.
