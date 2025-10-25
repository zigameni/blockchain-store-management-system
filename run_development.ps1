# Start database and ganache-cli in Docker
Start-Process docker -ArgumentList "compose","up","database","ganache-cli","adminer"

# Wait for services to be ready
Read-Host -Prompt "Press Enter when database and ganache-cli are ready..."

# Activate virtual environment (if you have one)
# .\venv\Scripts\activate.ps1

# Set environment variables for local development
$env:DATABASE_USERNAME = "root"
$env:DATABASE_PASSWORD = "root"
$env:DATABASE_URL = "localhost"
$env:DATABASE_NAME = "store_database"
$env:BLOCKCHAIN_URL = "http://127.0.0.1:8545"
$env:JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"

# Start authentication service on port 5000
Write-Host "Starting authentication service on port 5000..." -ForegroundColor Green
$env:PORT = "5000"
Start-Process python -ArgumentList "authentication/authentication.py"

# Start owner service on port 5001
Write-Host "Starting owner service on port 5001..." -ForegroundColor Green
$env:PORT = "5001"
Start-Process python -ArgumentList "owner/owner.py"

# Start customer service on port 5002
Write-Host "Starting customer service on port 5002..." -ForegroundColor Green
$env:PORT = "5002"
Start-Process python -ArgumentList "customer/customer.py"

# Start courier service on port 5003
Write-Host "Starting courier service on port 5003..." -ForegroundColor Green
$env:PORT = "5003"
Start-Process python -ArgumentList "courier/courier.py"

Write-Host "`nAll services started!" -ForegroundColor Cyan
Write-Host "Authentication: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Owner: http://localhost:5001" -ForegroundColor Yellow
Write-Host "Customer: http://localhost:5002" -ForegroundColor Yellow
Write-Host "Courier: http://localhost:5003" -ForegroundColor Yellow
Write-Host "Adminer: http://localhost:8080" -ForegroundColor Yellow
Write-Host "Ganache: http://localhost:8545" -ForegroundColor Yellow

Read-Host -Prompt "`nPress Enter to stop all services"

# Cleanup
docker compose down