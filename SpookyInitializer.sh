#!/bin/bash
clear
echo "=================================================="
echo "       SPOOKY SERVICE - LINUX NODE INITIALIZER   "
echo "=================================================="
echo ""

# Gather hardware attributes (Motherboard DMI serial or machine ID fallback)
BOARD_SERIAL=$(cat /sys/class/dmi/id/board_serial 2>/dev/null || cat /etc/machine-id 2>/dev/null || hostname)
CPU_INFO=$(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d':' -f2 || echo "Generic-CPU")

# Generate unique localized cryptographic hash
RAW_STRING="${BOARD_SERIAL}-${CPU_INFO}-SPK"
HASH_KEY=$(echo -n "$RAW_STRING" | sha256sum | awk '{print $1}' | cut -c1-24 | tr '[:lower:]' '[:upper:]')
SPOOKY_KEY="SPK-LNX-${HASH_KEY:0:4}-${HASH_KEY:4:4}-${HASH_KEY:8:4}-${HASH_KEY:12:4}"

# Establish local secure cache directory
CACHE_DIR="$HOME/.config/spooky"
mkdir -p "$CACHE_DIR"
echo "$SPOOKY_KEY" > "$CACHE_DIR/node_cache.dat"

echo "[+] Hardware attributes queried successfully."
echo "[+] Local node cache written to: $CACHE_DIR/node_cache.dat"
echo ""
echo "--------------------------------------------------"
echo "YOUR SPOOKY NODE KEY:"
echo "$SPOOKY_KEY"
echo "--------------------------------------------------"
echo ""
read -p "Initialization complete. Press [Enter] to close..."