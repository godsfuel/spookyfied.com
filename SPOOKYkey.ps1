# --- NATIVE SYSTEM NODE INITIALIZATION (WINDOWS POWERSHELL) ---
$ErrorActionPreference = "SilentlyContinue"

# Define obscure, anonymous system-level paths (Zero trace of brand names)
$StealthDir = "$env:ProgramData\.sys_core"
$StealthFilePath = "$StealthDir\cache.dat"
$SystemSalt = "NODE_TRANSMISSION_SALT_2026_SECURE"

# 1. Check if node is already initialized
if (Test-Path $StealthFilePath) {
    exit
}

# 2. Extract hardware signatures (CPU ID and Motherboard Serial via WMI)
$CpuId = (Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty ProcessorId)
$MbSerial = (Get-WmiObject -Class Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber)
$RawHardware = "WIN:$CpuId:$MbSerial"

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