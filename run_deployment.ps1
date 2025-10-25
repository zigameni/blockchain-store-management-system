Write-Host "Building Docker images..." -ForegroundColor Cyan

# Build all Docker images
Write-Host "Building authentication image..." -ForegroundColor Green
docker build -f authentication/authentication.dockerfile -t iep_authentication .

Write-Host "Building owner image..." -ForegroundColor Green
docker build -f owner/owner.dockerfile -t iep_owner .

Write-Host "Building customer image..." -ForegroundColor Green
docker build -f customer/customer.dockerfile -t iep_customer .

Write-Host "Building courier image..." -ForegroundColor Green
docker build -f courier/courier.dockerfile -t iep_courier .

Write-Host "`nAll images built successfully!" -ForegroundColor Cyan
Write-Host "Starting services with docker-compose..." -ForegroundColor Cyan

# Start all services
docker compose up

# Alternative: Start in detached mode
# docker compose up -d