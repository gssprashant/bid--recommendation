param(
    [string]$Image = "REPLACE_WITH_IMAGE:latest",
    [string]$Namespace = "default"
)

Write-Host "Deploying image: $Image to namespace: $Namespace"

# Create or update secret (interactive if FRED_API_KEY not set)
if (-not $env:FRED_API_KEY) {
    Write-Host "Environment variable FRED_API_KEY not set. Skipping secret creation. Create secret manually or set env var before running."
} else {
    kubectl -n $Namespace create secret generic gss-bid-secrets --from-literal=FRED_API_KEY=$env:FRED_API_KEY --dry-run=client -o yaml | kubectl apply -f -
}

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Patch image
kubectl -n $Namespace set image deployment/gss-bid-model gss-bid-model=$Image --record

Write-Host "Deployment applied. Use 'kubectl get pods' to check status."
