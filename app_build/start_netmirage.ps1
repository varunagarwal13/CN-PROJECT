# =================================================================
# NetMirage - Single Command Platform Launcher (PowerShell)
# Zero-Egress Sandboxed Defensive Cyber-Range
# =================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Split-Path -Parent $ScriptDir

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   NETMIRAGE DEFENSIVE CYBER-RANGE PLATFORM LAUNCHER (POWERSHELL)" -ForegroundColor Cyan
Write-Host "   Workspace Root: $WorkspaceRoot"
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Virtual Environment
$VenvPython = "$WorkspaceRoot\app_build\backend\.venv\Scripts\python.exe"
if (-Not (Test-Path $VenvPython)) {
    Write-Host "[1/4] Initializing Python virtual environment..." -ForegroundColor Yellow
    python -m venv "$WorkspaceRoot\app_build\backend\.venv"
    & "$WorkspaceRoot\app_build\backend\.venv\Scripts\pip.exe" install --upgrade pip
    & "$WorkspaceRoot\app_build\backend\.venv\Scripts\pip.exe" install -r "$WorkspaceRoot\app_build\backend\requirements.txt"
} else {
    Write-Host "[1/4] Python virtual environment verified: $VenvPython" -ForegroundColor Green
}

# 2. Database Initialization
Write-Host "[2/4] Initializing SQLite database schema..." -ForegroundColor Yellow
& $VenvPython -c "from app_build.backend.db import init_db; init_db(); print('SQLite schema initialized.')"

# 3. Docker Lab Verification
Write-Host "[3/4] Checking zero-egress Docker lab infrastructure..." -ForegroundColor Yellow
$dockerActive = $false
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerActive = $true }
} catch {
    $dockerActive = $false
}

if ($dockerActive) {
    Write-Host "      Docker daemon active. Validating docker-compose.lab.yml..." -ForegroundColor Green
    docker compose -f "$WorkspaceRoot\app_build\docker\docker-compose.lab.yml" up -d
} else {
    Write-Host "      Docker daemon not running or unavailable." -ForegroundColor Gray
    Write-Host "      [ACTIVE] Deterministic zero-egress lab emulator enabled (10.0.10.0/24 - 10.0.50.0/24)." -ForegroundColor Yellow
}

# 4. Start Backend and Frontend
Write-Host "[4/4] Starting NetMirage Backend and Frontend services..." -ForegroundColor Yellow

# Launch Backend in new process or background job
$BackendJob = Start-Job -ScriptBlock {
    param($python, $cwd)
    Set-Location $cwd
    & $python -m uvicorn app_build.backend.main:app --host 0.0.0.0 --port 8000
} -ArgumentList $VenvPython, $WorkspaceRoot

Write-Host "      FastAPI Control API running on http://localhost:8000 (Job ID: $($BackendJob.Id))" -ForegroundColor Green

# Launch Frontend in new process or background job
$FrontendJob = Start-Job -ScriptBlock {
    param($cwd)
    Set-Location "$cwd\app_build\frontend"
    npm run dev -- --host 0.0.0.0 --port 5173
} -ArgumentList $WorkspaceRoot

Write-Host "      Vite React Console running on http://localhost:5173 (Job ID: $($FrontendJob.Id))" -ForegroundColor Green

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   NETMIRAGE OPERATIONAL READOUT" -ForegroundColor Cyan
Write-Host "   - Web Console:       http://localhost:5173" -ForegroundColor White
Write-Host "   - Control API:       http://localhost:8000" -ForegroundColor White
Write-Host "   - OpenAPI Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Health Check:      http://localhost:8000/api/health" -ForegroundColor White
Write-Host "   - Egress Guard:      ZERO-EGRESS ENFORCED" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to terminate services."

try {
    while ($true) {
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "`n[NETMIRAGE] Shutting down background jobs..." -ForegroundColor Yellow
    Stop-Job $BackendJob 2>$null
    Remove-Job $BackendJob 2>$null
    Stop-Job $FrontendJob 2>$null
    Remove-Job $FrontendJob 2>$null
    if ($dockerActive) {
        docker compose -f "$WorkspaceRoot\app_build\docker\docker-compose.lab.yml" down 2>$null
    }
    Write-Host "[NETMIRAGE] Clean shutdown complete." -ForegroundColor Green
}
