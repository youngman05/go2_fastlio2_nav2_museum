#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SDK_DIR="${ROOT_DIR}/third_party/unitree_sdk2_python"

if [[ ! -d "${SDK_DIR}" ]]; then
  echo "unitree_sdk2_python is missing. Run 'make setup' first."
  exit 1
fi

echo "Installing Unitree SDK2 Python package from ${SDK_DIR}"

if ! python3 -c "import cyclonedds" >/dev/null 2>&1; then
  cat <<'EOF'
cyclonedds is not available in the current Python environment.
Install CycloneDDS first, for example:

  cd ~
  git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x
  cd cyclonedds
  mkdir -p build install
  cd build
  cmake .. -DCMAKE_INSTALL_PREFIX=../install
  cmake --build . --target install
  export CYCLONEDDS_HOME=~/cyclonedds/install

Then rerun:

  make setup-unitree-sdk
EOF
  exit 1
fi

python3 -m pip install -e "${SDK_DIR}"
echo "unitree_sdk2py installed"
