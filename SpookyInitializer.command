#!/bin/bash
clear
echo "=================================================="
echo "       SPOOKY SERVICE - MACOS NODE INITIALIZER   "
echo "=================================================="
echo ""

# Gather macOS Hardware UUID
HW_UUID=$(system_profiler SPHardwareDataType 2>/dev/null | grep "Hardware UUID" | awk '{print $3}')
if [ -z "$HW_UUID" ]; then
    HW_UUID=$(ioreg -rd1 -c "IOPlatformExpertDevice" | grep "IOPlatformUUID" | awk '{print $3}' | tr -d '"')
fi

# Generate unique localized cryptographic hash
RAW_STRING="${HW_UUID:-MAC-NODE}-SPK"
HASH_KEY=$(echo -n "$RAW_STRING" | shasum -a 256 | awk '{print $1}' | cut -c1-24 | tr '[:lower:]' '[:upper:]')
SPOOKY_KEY="SPK-MAC-${HASH_KEY:0:4}-${HASH_KEY:4:4}-${HASH_KEY:8:4}-${HASH_KEY:12:4}"

# Establish local secure cache directory in User Library
CACHE_DIR="$HOME/Library/Application Support/SpookyService"
mkdir -p "$CACHE_DIR"
echo "$SPOOKY_KEY" > "$CACHE_DIR/node_cache.dat"

echo "[+] System hardware attributes bound successfully."
echo "[+] Local node cache written to Application Support."
echo ""
echo "--------------------------------------------------"
echo "YOUR SPOOKY NODE KEY:"
echo "$SPOOKY_KEY"
echo "--------------------------------------------------"
echo ""
read -p "Initialization complete. Press [Return] to close..."