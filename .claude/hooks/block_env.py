#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

if ".env" in path:
    print(
        "BLOQUEADO POR POLITICA DEL EQUIPO: no se permite escribir en archivos .env. "
        "Este gate es deterministico y no se puede saltar, ni con --dangerously-skip-permissions.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
