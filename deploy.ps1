# Build and deploy script for kind (PowerShell)
Write-Host "Building Docker image..."
docker build -t bid-recommendation:latest .

Write-Host "Creating kind cluster..."
kind create cluster --config kind-config.yaml

Write-Host "Loading image into kind..."
kind load docker-image bid-recommendation:latest

Write-Host "Applying Kubernetes manifests..."
kubectl apply -f k8s/

Write-Host "Waiting for deployment to be ready..."
kubectl wait --for=condition=ready pod -l app=bid-recommendation --timeout=120s

Write-Host "Getting service URL..."
kubectl get svc bid-recommendation

Write-Host "Deployment complete! The API should be available at http://localhost:80"