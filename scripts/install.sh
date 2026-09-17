#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ALD // INSTALL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

if [[ ! -f "$ROOT/ald/ald.py" ]]; then
    echo "[ALD] Invalid Aldernix tree: ald/ald.py missing."
    exit 1
fi

if ! command -v pacman >/dev/null 2>&1; then
    echo "[ALD] Unsupported package manager."
    exit 2
fi

if command -v paru >/dev/null 2>&1; then
    echo "[ALD] paru detected."
else
    echo "[ALD] paru not found; pacman will be used for dependencies."
fi

if [[ ! -f "$ROOT/config/dependencies.json" ]]; then
    echo "[ALD] Dependency manifest missing."
    exit 3
fi

tmp_launcher="$(mktemp)"

cat > "$tmp_launcher" <<EOF
#!/usr/bin/env bash
set -euo pipefail

ROOT="$ROOT"

if [[ ! -f "\$ROOT/ald/ald.py" ]]; then
    echo "[ALD] Aldernix root not found: \$ROOT"
    echo "[ALD] Re-run scripts/install.sh from your Aldernix checkout."
    exit 1
fi

export PYTHONPATH="\$ROOT/ald\${PYTHONPATH:+:\$PYTHONPATH}"
exec /usr/bin/python "\$ROOT/ald/ald.py" "\$@"
EOF

sudo install -Dm755 "$tmp_launcher" /usr/local/bin/ald
rm -f "$tmp_launcher"

if [[ ! -f "$ROOT/VERSION" ]]; then
    printf '%s\n' '0.1.0-dev' > "$ROOT/VERSION"
fi

echo
echo "[+] ALD installed."
echo "[+] Root     : $ROOT"
echo "[+] Entrypoint: /usr/local/bin/ald"
echo
echo "[+] Commands:"
echo "    ald update --verify"
echo "    ald update"
