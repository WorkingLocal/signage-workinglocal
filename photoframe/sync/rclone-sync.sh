#!/bin/bash
# rclone-sync.sh — synchroniseer foto's van ai-node-i9 naar VPS
# Bronpad:  ai-node-i9:/mnt/fotos/frame  (via Tailscale SSH)
# Doelpad:  /data/photoframe/photos/
# Schedule: dagelijks 02:00 via cron (zie cron.d/photoframe-sync)
#
# Vereisten:
#   - rclone geinstalleerd op VPS
#   - SSH key /root/.ssh/photoframe_rclone (geen passphrase) geconfigureerd op ai-node-i9
#   - rclone config: zie /etc/rclone/photoframe.conf

set -euo pipefail

RCLONE_CONFIG="/etc/rclone/photoframe.conf"
SOURCE="ai-node-i9:/mnt/fotos/frame"
DEST="/data/photoframe/photos"
LOG_FILE="/var/log/photoframe-sync.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync gestart: $SOURCE → $DEST" >> "$LOG_FILE"

rclone sync \
  --config "$RCLONE_CONFIG" \
  --transfers 4 \
  --checkers 8 \
  --exclude ".zfs/**" \
  --exclude "*.tmp" \
  --log-file "$LOG_FILE" \
  --log-level INFO \
  "$SOURCE" "$DEST"

FOTO_COUNT=$(find "$DEST" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync klaar. Foto's aanwezig: $FOTO_COUNT" >> "$LOG_FILE"
