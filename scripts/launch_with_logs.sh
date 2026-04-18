#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-guide}"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="runtime-data/logs/${STAMP}-${MODE}"
mkdir -p "${LOG_DIR}"

echo "Launching mode: ${MODE}"
echo "Logs: ${LOG_DIR}"

exec > >(tee "${LOG_DIR}/stdout.log") 2> >(tee "${LOG_DIR}/stderr.log" >&2)

case "${MODE}" in
  slam)
    ros2 launch bringup system_slam.launch.py
    ;;
  nav)
    ros2 launch bringup system_nav.launch.py
    ;;
  guide)
    ros2 launch bringup system_guide.launch.py
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    exit 1
    ;;
esac
