# Start database and ganache-cli in Docker
Write-Host "Starting Docker services..." -ForegroundColor Cyan
Start-Process docker -ArgumentList "compose","up","database","ganache-cli","adminer"

# Wait for services to be ready
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "Services should be ready. Check Docker Desktop to confirm." -ForegroundColor Green
Read-Host -Prompt "Press Enter when database and ganache-cli are ready"

# Get the current directory for use in new terminals
$currentDir = Get-Location

# Array to store process objects
$processes = @()

# Start authentication service on port 5000
Write-Host "Starting authentication service on port 5000..." -ForegroundColor Green
$authCmd = "cd '$currentDir'; .\.venv\Scripts\Activate.ps1; `$env:PYTHONPATH='$currentDir'; `$env:DATABASE_USERNAME='root'; `$env:DATABASE_PASSWORD='root'; `$env:DATABASE_URL='localhost'; `$env:DATABASE_NAME='store_database'; `$env:BLOCKCHAIN_URL='http://127.0.0.1:8545'; `$env:JWT_SECRET_KEY='JWT_SECRET_DEV_KEY'; `$env:PORT='5000'; python authentication/authentication.py"
$processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", $authCmd -PassThru

Start-Sleep -Seconds 2

# Start owner service on port 5001
Write-Host "Starting owner service on port 5001..." -ForegroundColor Green
$ownerCmd = "cd '$currentDir'; .\.venv\Scripts\Activate.ps1; `$env:PYTHONPATH='$currentDir'; `$env:DATABASE_USERNAME='root'; `$env:DATABASE_PASSWORD='root'; `$env:DATABASE_URL='localhost'; `$env:DATABASE_NAME='store_database'; `$env:BLOCKCHAIN_URL='http://127.0.0.1:8545'; `$env:JWT_SECRET_KEY='JWT_SECRET_DEV_KEY'; `$env:PORT='5001'; python owner/owner.py"
$processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", $ownerCmd -PassThru

Start-Sleep -Seconds 2

# Start customer service on port 5002
Write-Host "Starting customer service on port 5002..." -ForegroundColor Green
$customerCmd = "cd '$currentDir'; .\.venv\Scripts\Activate.ps1; `$env:PYTHONPATH='$currentDir'; `$env:DATABASE_USERNAME='root'; `$env:DATABASE_PASSWORD='root'; `$env:DATABASE_URL='localhost'; `$env:DATABASE_NAME='store_database'; `$env:BLOCKCHAIN_URL='http://127.0.0.1:8545'; `$env:JWT_SECRET_KEY='JWT_SECRET_DEV_KEY'; `$env:PORT='5002'; python customer/customer.py"
$processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", $customerCmd -PassThru

Start-Sleep -Seconds 2

# Start courier service on port 5003
Write-Host "Starting courier service on port 5003..." -ForegroundColor Green
$courierCmd = "cd '$currentDir'; .\.venv\Scripts\Activate.ps1; `$env:PYTHONPATH='$currentDir'; `$env:DATABASE_USERNAME='root'; `$env:DATABASE_PASSWORD='root'; `$env:DATABASE_URL='localhost'; `$env:DATABASE_NAME='store_database'; `$env:BLOCKCHAIN_URL='http://127.0.0.1:8545'; `$env:JWT_SECRET_KEY='JWT_SECRET_DEV_KEY'; `$env:PORT='5003'; python courier/courier.py"
$processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", $courierCmd -PassThru

Write-Host "`nAll services started!" -ForegroundColor Cyan
Write-Host "Authentication: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Owner: http://localhost:5001" -ForegroundColor Yellow
Write-Host "Customer: http://localhost:5002" -ForegroundColor Yellow
Write-Host "Courier: http://localhost:5003" -ForegroundColor Yellow
Write-Host "Adminer: http://localhost:8080" -ForegroundColor Yellow
Write-Host "Ganache: http://localhost:8545" -ForegroundColor Yellow

Read-Host -Prompt "`nPress Enter to stop all services"

# Cleanup - Kill all PowerShell windows
Write-Host "Stopping all service windows..." -ForegroundColor Yellow
foreach ($process in $processes) {
    if (!$process.HasExited) {
        Stop-Process -Id $process.Id -Force
        Write-Host "Stopped process $($process.Id)" -ForegroundColor Gray
    }
}

# Stop Docker services
Write-Host "Stopping Docker services..." -ForegroundColor Yellow
docker compose down
Write-Host "Done!" -ForegroundColor Green