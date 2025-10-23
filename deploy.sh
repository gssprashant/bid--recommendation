# Build and deploy script for kind
echo "Building Docker image..."
docker build -t bid-recommendation:latest .

echo "Creating kind cluster..."
kind create cluster --config kind-config.yaml

echo "Loading image into kind..."
kind load docker-image bid-recommendation:latest

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/

echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=ready pod -l app=bid-recommendation --timeout=120s

echo "Getting service URL..."
kubectl get svc bid-recommendation

echo "Deployment complete! The API should be available at http://localhost:80"