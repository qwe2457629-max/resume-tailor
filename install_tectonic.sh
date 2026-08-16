#!/usr/bin/env bash
# Install the Tectonic LaTeX compiler to ~/.local/bin.
#
# Tectonic is a single self-contained binary that downloads LaTeX packages
# on demand, so there is no TeX Live install and no admin password needed.
#
# Usage: bash install_tectonic.sh

set -euo pipefail

BIN_DIR="${HOME}/.local/bin"
TARGET="${BIN_DIR}/tectonic"

if [ -x "${TARGET}" ]; then
    echo "Already installed: $("${TARGET}" --version)"
    exit 0
fi

case "$(uname -s)" in
    Darwin) os="apple-darwin" ;;
    Linux)  os="unknown-linux-gnu" ;;
    *) echo "Unsupported OS: $(uname -s)" >&2; exit 1 ;;
esac

case "$(uname -m)" in
    arm64|aarch64) arch="aarch64" ;;
    x86_64|amd64)  arch="x86_64" ;;
    *) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

echo "Looking up the latest Tectonic release for ${arch}-${os}..."
url=$(curl -fsSL https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest \
    | python3 -c "
import json, sys
want = '${arch}-${os}'
for asset in json.load(sys.stdin)['assets']:
    if want in asset['name'] and asset['name'].endswith('.tar.gz'):
        print(asset['browser_download_url'])
        break
")

if [ -z "${url}" ]; then
    echo "No release asset found for ${arch}-${os}." >&2
    exit 1
fi

tmp=$(mktemp -d)
trap 'rm -rf "${tmp}"' EXIT

echo "Downloading ${url}"
curl -fsSL -o "${tmp}/tectonic.tar.gz" "${url}"
tar xzf "${tmp}/tectonic.tar.gz" -C "${tmp}"

mkdir -p "${BIN_DIR}"
mv "${tmp}/tectonic" "${TARGET}"
chmod +x "${TARGET}"

echo "Installed: $("${TARGET}" --version)"
echo
echo "${BIN_DIR} may not be on your PATH. Either call it by full path:"
echo "    ${TARGET} resume.tex"
echo "or add this to your shell profile:"
echo "    export PATH=\"\${HOME}/.local/bin:\${PATH}\""
echo
echo "The first compile downloads LaTeX packages and needs a network connection."
