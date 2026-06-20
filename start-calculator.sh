#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${HOME}/.cache"
LOG_FILE="${LOG_DIR}/matrix-calculator.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "${LOG_DIR}"
cd "${APP_DIR}"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] start"
  echo "PWD=${PWD}"
  echo "DISPLAY=${DISPLAY:-<unset>}"
  echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-<unset>}"
  echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-<unset>}"
} >> "${LOG_FILE}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python nicht gefunden: ${PYTHON_BIN}" >> "${LOG_FILE}"
  if command -v kdialog >/dev/null 2>&1; then
    kdialog --error "Python wurde nicht gefunden: ${PYTHON_BIN}" >/dev/null 2>&1 || true
  fi
  exit 1
fi

if ! command "${PYTHON_BIN}" "${APP_DIR}/calculator.py" >> "${LOG_FILE}" 2>&1; then
  if command -v kdialog >/dev/null 2>&1; then
    kdialog --error "Matrix Calculator konnte nicht gestartet werden.\n\nLog: ${LOG_FILE}" >/dev/null 2>&1 || true
  elif command -v xmessage >/dev/null 2>&1; then
    xmessage "Matrix Calculator konnte nicht gestartet werden. Log: ${LOG_FILE}" >/dev/null 2>&1 || true
  fi
  exit 1
fi
