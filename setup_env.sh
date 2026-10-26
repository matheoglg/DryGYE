#!/usr/bin/env bash
# DryGYE - environment installer for Linux / macOS (Windows users: setup_env.bat).
#
# Usage:
#   ./setup_env.sh                    conda/mamba/micromamba if found, otherwise python venv
#   ./setup_env.sh --venv             force python -m venv + requirements.txt
#   ./setup_env.sh --conda            force conda-family tool (fails if none is installed)
#   ./setup_env.sh --name NAME        environment name (default: drygye)
#   ./setup_env.sh --with-telegram    also install requirements-optional.txt
#   ./setup_env.sh --skip-net-check   skip the Open-Meteo / OpenStreetMap test
#   ./setup_env.sh --recreate         delete the environment and build it again
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

MODE="auto"
ENV_NAME="drygye"
WITH_TELEGRAM=0
NET_CHECK=1
RECREATE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --venv) MODE="venv" ;;
    --conda) MODE="conda" ;;
    --name) ENV_NAME="${2:?--name needs a value}"; shift ;;
    --with-telegram) WITH_TELEGRAM=1 ;;
    --skip-net-check) NET_CHECK=0 ;;
    --recreate) RECREATE=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

for f in environment.yml requirements.txt requirements-optional.txt check_env.py; do
  [ -f "$f" ] || { echo "Missing file '$f' next to this script." >&2; exit 1; }
done

step() { printf '\n==> %s\n' "$1"; }

CONDA_TOOL=""
for t in micromamba mamba conda; do
  if command -v "$t" >/dev/null 2>&1; then CONDA_TOOL="$t"; break; fi
done

if [ "$MODE" = "auto" ]; then
  if [ -n "$CONDA_TOOL" ]; then MODE="conda"; else MODE="venv"; fi
fi

if [ "$MODE" = "conda" ]; then
  [ -n "$CONDA_TOOL" ] || { echo "No conda, mamba or micromamba found. Use --venv or install Miniconda." >&2; exit 1; }
  step "Using $CONDA_TOOL"
  env_exists() {
    local names
    names="$("$CONDA_TOOL" env list 2>/dev/null | awk '{print $1}')" || true
    grep -qx "$ENV_NAME" <<<"$names"
  }
  if env_exists && [ "$RECREATE" -eq 1 ]; then
    step "Removing environment '$ENV_NAME' (--recreate)"
    "$CONDA_TOOL" env remove -y -n "$ENV_NAME"
  fi
  if env_exists; then
    step "Updating environment '$ENV_NAME' from environment.yml"
    if [ "$CONDA_TOOL" = "micromamba" ]; then
      "$CONDA_TOOL" install -y -n "$ENV_NAME" -f environment.yml
    else
      "$CONDA_TOOL" env update -n "$ENV_NAME" -f environment.yml --prune
    fi
  else
    step "Creating environment '$ENV_NAME' (5-15 minutes)"
    if [ "$CONDA_TOOL" = "micromamba" ]; then
      "$CONDA_TOOL" create -y -n "$ENV_NAME" -f environment.yml
    else
      "$CONDA_TOOL" env create -n "$ENV_NAME" -f environment.yml
    fi
  fi
  RUN=("$CONDA_TOOL" run -n "$ENV_NAME")
  PY=("${RUN[@]}" python)
else
  step "Looking for Python 3.10+"
  PYBIN=""
  for c in python3.11 python3.12 python3.10 python3 python; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PYBIN="$c"; break
    fi
  done
  [ -n "$PYBIN" ] || { echo "Python 3.10+ not found." >&2; exit 1; }
  if [ "$RECREATE" -eq 1 ]; then rm -rf .venv; fi
  [ -d .venv ] || { step "Creating .venv with $PYBIN"; "$PYBIN" -m venv .venv; }
  PY=(.venv/bin/python)
  step "Installing libraries with pip (several minutes)"
  "${PY[@]}" -m pip install --upgrade pip
  "${PY[@]}" -m pip install -r requirements.txt
fi

if [ "$WITH_TELEGRAM" -eq 1 ]; then
  step "Installing optional extras (Telegram)"
  "${PY[@]}" -m pip install -r requirements-optional.txt
fi

step "Verifying the installation"
CHECK_ARGS=(check_env.py)
[ "$NET_CHECK" -eq 1 ] && CHECK_ARGS+=(--net)
"${PY[@]}" "${CHECK_ARGS[@]}"

echo
echo "Environment ready."
if [ "$MODE" = "conda" ]; then
  echo "Activate:  $CONDA_TOOL activate $ENV_NAME"
else
  echo "Activate:  source .venv/bin/activate"
fi
echo "Check a DEM:  python check_env.py --dem path/to/file.tif"
