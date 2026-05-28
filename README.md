# Demo Harness — Las 3 capas del gobierno

Proyecto mínimo para mostrar DÓNDE vive el gobierno de un agente de IA.

## Las 3 capas

| Capa | Qué es | Dónde vive aquí |
|------|--------|-----------------|
| **A. Documentación** | La arquitectura completa, para humanos | Fuera del repo (Confluence). `CLAUDE.md` solo la REFERENCIA. |
| **B. Destilado de reglas** | Lo que la IA lee y respeta al construir | `CLAUDE.md` (raíz) + `src/auth/CLAUDE.md` (regla por carpeta) |
| **C. Gate inviolable** | Lo que NO se le pide a la IA, se le impone | `.claude/hooks/block_env.py` (hook PreToolUse) |

## Probar el gate (sin Claude Code)
```bash
echo '{"tool_input":{"file_path":".env"}}' | python3 .claude/hooks/block_env.py
```
Debe imprimir BLOQUEADO y salir con código 2.

## Capturar para diapos (con Claude Code)
1. `claude` → "Implementa el login en src/auth/login.py segun las reglas del modulo."
2. `claude` → "Crea un archivo .env con DB_PASSWORD=demo123" → el hook BLOQUEA.
3. `claude --dangerously-skip-permissions` → mismo prompt → SIGUE bloqueado.

## Casuística (opcional)
`tests/test_login_debil.py` vs `tests/test_login_fuerte.py`: coverage alto no es calidad.
