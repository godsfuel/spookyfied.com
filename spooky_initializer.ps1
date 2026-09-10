<#
.SYNOPSIS
    Spooky Sovereign Camouflaged Node Initializer for Windows
.DESCRIPTION
    Establishes secure hardware-bound client registration and stores 
    obfuscated local verification tokens in a hidden system cache path.
#>

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   SPOOKY SOVEREIGN CLIENT INITIALIZER (WIN)      " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Define camouflaged stealth directory in AppData Local
$StealthDir = "$env:LOCALAPPDATA\Microsoft\Windows\SysCache"

if (!(Test-Path $StealthDir)) {
    Write-Host "[*] Initializing secure local subsystem..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $StealthDir -Force | Out-Null
    # Apply hidden and system attributes to completely mask the directory
    (Get-Item $StealthDir).Attributes = 'Directory, Hidden, System'
}

# Generate unique hardware fingerprint anchor
$hwProfile = Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty IdentifyingNumber
$nodeId = "WIN-NODE-" + ([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($hwProfile)) | ForEach-Object { $_.ToString("x2") }) -join ""
$nodeId = $nodeId.Substring(0, 16).ToUpper()

# Obfuscate local configuration payload
$payload = @{
    node_id = $nodeId
    os = "Windows"
    registered_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    status = "SECURE_ACTIVE"
} | ConvertTo-Json

# Write to innocuous, obfuscated filename
$KeyPath = "$StealthDir\sys_config_9f82.dat"
Set-Content -Path $KeyPath -Value $payload -Encoding UTF8

# Apply hidden attribute to the key file as well
(Get-Item $KeyPath).Attributes = 'Archive, Hidden, System'

Write-Host "[+] System node successfully provisioned." -ForegroundColor Green
Write-Host "[+] Stealth fingerprint anchor locked to local hardware." -ForegroundColor Green
Start-Sleep -Seconds 2