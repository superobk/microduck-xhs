#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo 'Please install Python 3 first.' >&2; exit 1; }
python3 tools/build.py "$@"
python3 tools/test_project.py
if [ "$(uname -s)" = Darwin ]; then open publisher.html; else printf 'Open publisher.html in a browser.\n'; fi
