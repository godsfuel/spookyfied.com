# --- NATIVE SYSTEM NODE INITIALIZATION (WINDOWS POWERSHELL) ---
$ErrorActionPreference = "SilentlyContinue"

# Define obscure, anonymous system-level paths
$StealthDir = "$env:ProgramData\.sys_core"
$StealthFilePath = "$StealthDir\cache.dat"
$SystemSalt = "NODE_TRANSMISSION_SALT_2026_SECURE"

Clear-Host
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         SPOOKY SERVICE - NODE INITIALIZER             " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check if node is already initialized
if (Test-Path $StealthFilePath) {
    Write-Host "[+] Terminal Node already initialized and spookified!" -ForegroundColor Green
    Write-Host "[+] Hardware-bound cryptographic key is active in cache." -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host "[*] Extracting hardware signatures..." -ForegroundColor Yellow

# 2. Extract hardware signatures (CPU ID and Motherboard Serial via WMI)
$CpuId = (Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty ProcessorId)
$MbSerial = (Get-WmiObject -Class Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber)

# Fixed string concatenation to prevent parser errors
$RawHardware = "WIN:" + $CpuId + ":" + $MbSerial

Write-Host "[*] Generating cryptographic hardware-bound seed..." -ForegroundColor Yellow

# 3. Generate SHA-256 cryptographic hash combined with system salt
$CombinedData = $RawHardware + $SystemSalt
$Bytes = [System.Text.Encoding]::UTF8.GetBytes($CombinedData)
$Sha = [System.Security.Cryptography.SHA256]::Create()
$HashBytes = $Sha.ComputeHash($Bytes)

# 4. Create the hidden system directory if it doesn't exist
if (!(Test-Path $StealthDir)) {
    New-Item -ItemType Directory -Force -Path $StealthDir | Out-Null
}

# 5. Lock the key away in the secure cache file silently
[System.IO.File]::WriteAllBytes($StealthFilePath, $HashBytes)

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "         SUCCESS: NODE SUCCESSFULLY SPOOKIFIED!        " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Your hardware-bound cryptographic key has been locked" -ForegroundColor White
Write-Host "into your local system cache. This terminal node is now" -ForegroundColor White
Write-Host "ready to securely receive dedicated media streams." -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")