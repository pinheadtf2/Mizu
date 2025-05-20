#!/usr/bin/env bash
set -e  # Exit immediately if any command fails

# Name of your virtualenv folder
VENV_DIR=".venv"

# Python executable to use
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating virtual environment in ${VENV_DIR}..."
  python3 -m venv "${VENV_DIR}"
fi

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [ -f requirements.txt ]; then
  echo "Installing/updating dependencies from requirements.txt..."
  "${PIP}" install --upgrade pip
  "${PIP}" install -r requirements.txt
else
  echo "requirements.txt not found—skipping dependency installation."
fi

echo "Running code..."
exec "${PYTHON}" main.py "$@"
