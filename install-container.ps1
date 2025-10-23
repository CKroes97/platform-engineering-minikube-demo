# ===========================================
# Fedora 41 WSL Installer - PowerShell
# ===========================================
$image = "fedora:41"
$distroName = "Fedora-41-llm-demo"

# Check WSL is installed
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] WSL is not installed." -ForegroundColor Red
    Write-Host "Please install WSL first:" -ForegroundColor Yellow
    Write-Host "    wsl --install"
    exit 1
}

# Capture WSL status as plain text and strip ANSI / control chars
$raw = wsl.exe --status 2>&1 | Out-String

# Remove ANSI CSI sequences and other non-printable control chars (keep CR/LF)
$output = ($raw -replace '\x1B\[[0-9;]*[A-Za-z]', '') -replace '[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+', ''

# Filter the cleaned WSL status output for the line that starts with "Default Version :"
$defaultVersionLine = ($output -split "`r?`n" | Where-Object { $_ -match '^\s*Default\s+Version\s*:' } | Select-Object -First 1)

if (-not $defaultVersionLine) {
    Write-Host "[ERROR] Could not find a line beginning with 'Default Version :' in WSL status output." -ForegroundColor Red
    Write-Host "WSL status output:" -ForegroundColor Yellow
    Write-Host $output
    exit 1
}

# Extract the version number
$wslVersion = ($defaultVersionLine -split ":")[1].Trim()

if ($wslVersion -ne "2") {
    Write-Host "[ERROR] Your default WSL version is $wslVersion, not 2." -ForegroundColor Red
    Write-Host "Please run: wsl --set-default-version 2" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Default WSL version is 2." -ForegroundColor Green

# Verify Docker CLI is available on PATH
$getDocker = Get-Command docker -ErrorAction SilentlyContinue

if ($getDocker) {
    Write-Host "[OK] Docker is available" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Docker CLI ('docker') is not installed or not on PATH." -ForegroundColor Red
    Write-Host "Install Docker Desktop and ensure 'docker' is on your PATH:" -ForegroundColor Yellow
    exit 1
}

# Verify Docker daemon is running (can connect to the engine)
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker daemon is running and accessible." -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Docker daemon does not appear to be running or is not accessible." -ForegroundColor Red
    Write-Host "Start Docker Desktop (or your Docker daemon) and ensure the 'docker' CLI can talk to the daemon." -ForegroundColor Yellow
    exit 1
}
# Determine script directory for output location
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
if ([string]::IsNullOrWhiteSpace($scriptDir)) { $scriptDir = Get-Location }


$tarballPath = Join-Path -Path $scriptDir -ChildPath "fedora-41.tar"

Write-Host "[INFO] Pulling image $image ..." -ForegroundColor Cyan
$pullOutput = & docker pull $image 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to pull image $image." -ForegroundColor Red
    Write-Host $pullOutput -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Creating temporary container from $image ..." -ForegroundColor Cyan
$createOutput = & docker create $image 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create container from $image." -ForegroundColor Red
    Write-Host $createOutput -ForegroundColor Yellow
    exit 1
}
$containerId = $createOutput.Trim()

try {
    Write-Host "[INFO] Exporting container filesystem to $tarballPath ..." -ForegroundColor Cyan
    $exportOutput = & docker export -o $tarballPath $containerId 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to export container filesystem." -ForegroundColor Red
        Write-Host $exportOutput -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[OK] Fedora 41 rootfs exported to: $tarballPath" -ForegroundColor Green
}
finally {
    # Ensure the temporary container is removed
    if ($containerId) {
        & docker rm $containerId 2>$null | Out-Null
    }
}

# Import the exported tarball into WSL as a new distro and configure a default non-root user
$installPath = Join-Path -Path $HOME -ChildPath $distroName

# Ensure distro name not already registered
$registered = & wsl.exe --list --quiet 2>$null | Out-String
# Strip ANSI CSI sequences and non-printable control characters (preserve CR/LF)
$registered = ($registered -replace '\x1B\[[0-9;]*[A-Za-z]', '') -replace '[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+', ''

if ($registered -match "(?m)^\s*$distroName\s*$") {
    Write-Host "[ERROR] A WSL distro named '$distroName' is already registered." -ForegroundColor Red
    Write-Host "Unregister it first (wsl --unregister $distroName) or choose a different name." -ForegroundColor Yellow
    exit 1
}

# Ensure install directory does not already exist
if (Test-Path -LiteralPath $installPath) {
    Write-Host "[ERROR] Install directory already exists: $installPath" -ForegroundColor Red
    Write-Host "Remove or choose a different location." -ForegroundColor Yellow
    exit 1
}

# Create install directory
try {
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
}
catch {
    Write-Host "[ERROR] Failed to create install directory: $installPath" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Importing tarball into WSL as '$distroName' (install path: $installPath) ..." -ForegroundColor Cyan
$importArgs = @('--import', $distroName, $installPath, $tarballPath, '--version', '2')
$importOutput = & wsl.exe @importArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] wsl --import failed." -ForegroundColor Red
    Write-Host $importOutput -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Imported WSL distro: $distroName" -ForegroundColor Green

Write-Host "[INFO] You can start the new distro with: wsl -d $distroName" -ForegroundColor Cyan

# Remove the exported tarball if it exists
if (Test-Path -LiteralPath $tarballPath) {
    try {
        Remove-Item -LiteralPath $tarballPath -Force -ErrorAction Stop
        Write-Host "[OK] Cleanup - removed tarball: $tarballPath" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed cleanup remove tarball: $tarballPath" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Yellow
        exit 1
    }
}