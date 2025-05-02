# ================================================
# 🛠 Windows Build Script for Python + Electron
# ================================================

$ErrorActionPreference = "Stop"

# Set paths (adjust if needed)
$RootDir = Resolve-Path "$PSScriptRoot\.."
$VenvActivate = "$RootDir\venv\Scripts\activate.ps1"
$SpecFile = "$RootDir\run.spec"
$DistBinary = "$RootDir\dist\run.exe"
$ElectronDir = "$RootDir\electron"
$ElectronBinary = "$ElectronDir\run.exe"

Write-Host "Step 1: Activating virtual environment..."
& $VenvActivate

Write-Host "Step 2: Building Python binary..."
pyinstaller $SpecFile

Write-Host "Step 3: Copying binary to Electron app..."
Copy-Item $DistBinary $ElectronBinary -Force

Write-Host "Step 4: Building Electron app for Windows..."
Set-Location $ElectronDir
npm run dist

Write-Host "✅ Build complete!" -ForegroundColor Green
