#!/bin/bash
# ==========================================================
#   SPOOKY SOVEREIGN CLIENT INITIALIZER (Linux)
# ==========================================================

echo "=================================================="
echo "   SPOOKY SOVEREIGN CLIENT INITIALIZER (Linux)    "
echo "=================================================="

# Define camouflaged local share hidden directory
STEALTH_DIR="$HOME/.local/share/.sys_cache"
mkdir -p "$STEALTH_DIR"

# Generate machine fingerprint
MACHINE_ID=$(cat /etc/machine-id 2>/dev/null || hostname)
NODE_ID="LIN-NODE-$(echo -n "$MACHINE_ID" | sha256sum | head -c 16 | tr '[:lower:]' '[:upper:']')"

# Write obfuscated payload
CONFIG_FILE="$STEALTH_DIR/sys_manifest_v2.bin"
cat << EOF > "$CONFIG_FILE"
{
    "node_id": "$NODE_ID",
    "os": "Linux",
    "status": "SECURE_ACTIVE"
}
EOF

chmod 600 "$CONFIG_FILE"

echo "[+] System node successfully provisioned."
echo "[+] Stealth credential secured."
sleep 2