#!/bin/bash
# ==========================================================
#   SPOOKY SOVEREIGN CLIENT INITIALIZER (macOS)
# ==========================================================

CLEAR_COLOR='\033[0m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'

echo -e "${CYAN}=================================================="
echo -e "   SPOOKY SOVEREIGN CLIENT INITIALIZER (macOS)    "
echo -e "==================================================${CLEAR_COLOR}"

# Define camouflaged dot-directory hidden inside Library Application Support
STEALTH_DIR="$HOME/Library/Application Support/.sys_cache"
mkdir -p "$STEALTH_DIR"

# Generate hardware-bound client ID
HW_UUID=$(ioreg -rd1 -c "IOPlatformExpertDevice" | grep "IOPlatformUUID" | awk -F'"' '{print $4}')
NODE_ID="MAC-NODE-$(echo -n "$HW_UUID" | shasum -a 256 | head -c 16 | tr '[:lower:]' '[:upper:']')"

# Write obfuscated config payload
CONFIG_FILE="$STEALTH_DIR/sys_manifest_v2.bin"
cat << EOF > "$CONFIG_FILE"
{
    "node_id": "$NODE_ID",
    "os": "macOS",
    "status": "SECURE_ACTIVE"
}
EOF

# Restrict file permissions to owner read/write only
chmod 600 "$CONFIG_FILE"

echo -e "${GREEN}[+] System node successfully provisioned.${CLEAR_COLOR}"
echo -e "${GREEN}[+] Stealth credential locked securely.${CLEAR_COLOR}"
sleep 2