#!/usr/bin/env bash
# Read-only inventory. Raw output may contain identifying data; do not publish unreviewed.
set -u
umask 077
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/evidence/raw/camera-$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$OUT"
{
  date -u
  uname -a
  cat /etc/os-release 2>/dev/null || true
  printf '\n=== Device tree model ===\n'
  tr -d '\0' </proc/device-tree/model 2>/dev/null || true
  printf '\n=== Memory ===\n'; free -h 2>/dev/null || true
  printf '\n=== Video nodes ===\n'; ls -l /dev/video* /dev/media* 2>/dev/null || true
  if command -v v4l2-ctl >/dev/null; then
    v4l2-ctl --list-devices
    for dev in /dev/video*; do
      [ -e "$dev" ] || continue
      printf '\n=== %s ===\n' "$dev"
      v4l2-ctl -d "$dev" --all
      v4l2-ctl -d "$dev" --list-formats-ext
    done
  else printf 'v4l2-ctl unavailable; not installed by this script.\n'; fi
  printf '\n=== Filtered kernel messages (permission may be denied) ===\n'
  dmesg 2>&1 | grep -Ei 'imx|ov[0-9]|camera|csi|v4l|isp|denied|permitted' || true
} >"$OUT/probe.txt" 2>&1
printf 'Saved %s/probe.txt\nRead-only collection; hardware success is NOT asserted.\n' "$OUT"
