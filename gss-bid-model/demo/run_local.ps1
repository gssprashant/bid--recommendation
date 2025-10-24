# Build and run demo container locally (PowerShell)
param(
    [string]$Image = 'gss-bid-demo:latest'
)

Write-Host "Building image $Image..."
docker build -t $Image -f demo/Dockerfile .

Write-Host "Running container..."
docker run --rm -p 8000:8000 --name gss-bid-demo $Image
