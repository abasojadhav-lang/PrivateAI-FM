# PowerShell Script to download and install Flutter SDK automatically using curl and tar
$ErrorActionPreference = "Stop"

$installDir = "C:\src"
if (!(Test-Path $installDir)) {
    Write-Host "Creating directory $installDir..."
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
}

# Clean up any existing corrupted zip file
$zipPath = "$installDir\flutter.zip"
if (Test-Path $zipPath) {
    Write-Host "Removing existing corrupted zip file..."
    Remove-Item -Path $zipPath -Force
}

Write-Host "Fetching latest stable Flutter version metadata..."
$metadataUrl = "https://storage.googleapis.com/flutter_infra_release/releases/releases_windows.json"
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $response = Invoke-RestMethod -Uri $metadataUrl
    $latestStable = $response.releases | Where-Object { $_.channel -eq "stable" } | Select-Object -First 1
    $downloadUrl = "https://storage.googleapis.com/flutter_infra_release/releases/" + $latestStable.archive
} catch {
    Write-Host "Error details: $_" -ForegroundColor Red
    Write-Error "Failed to fetch Flutter release metadata. Please check your internet connection."
    exit
}

Write-Host "Downloading Flutter SDK from $downloadUrl using curl..."
try {
    # Call native curl.exe which handles large files, modern TLS, and displays download progress.
    & curl.exe -L -o $zipPath $downloadUrl
} catch {
    Write-Host "Error details: $_" -ForegroundColor Red
    Write-Error "Failed to download Flutter SDK."
    exit
}

Write-Host "Extracting Flutter SDK to $installDir using tar..."
try {
    # Call native tar.exe for fast and reliable extraction.
    & tar.exe -xf $zipPath -C $installDir
} catch {
    Write-Host "Error details: $_" -ForegroundColor Red
    Write-Error "Extraction failed. Make sure you have enough disk space."
    exit
}

Write-Host "Cleaning up download files..."
Remove-Item -Path $zipPath -ErrorAction SilentlyContinue

Write-Host "Adding Flutter to User Environment PATH..."
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$flutterBin = "C:\src\flutter\bin"
if ($userPath -notlike "*flutter\bin*") {
    $newUserPath = $userPath + ";$flutterBin"
    [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
    Write-Host "Successfully added Flutter to PATH!"
} else {
    Write-Host "Flutter is already present in PATH."
}

Write-Host "========================================================="
Write-Host "Flutter Setup Completed Successfully!"
Write-Host "Please close and reopen your terminals / apps to reload PATH."
Write-Host "Run 'flutter doctor' in a new terminal to check other setup items."
Write-Host "========================================================="
