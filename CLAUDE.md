# Proyecto: Autenticación — Demo Harness

## Qué es esto
Módulo de inicio de sesión.
La arquitectura completa (diagramas, decisiones cloud/on-premise) vive en Confluence:
https://confluence.empresa/arquitectura-auth
NO la dupliques aquí. Este archivo solo contiene las reglas que la IA debe respetar siempre.

## Stack
- Python 3.11
- Tests: pytest

## Reglas no negociables (el destilado)
- Ningún dato sensible (contraseñas, tokens, datos personales) se guarda ni se
  registra en texto plano. Razón: cumplimiento regulatorio.
- Toda función pública lleva su test antes de darse por terminada.
- No se crean dependencias nuevas sin justificarlo.

## Lo que NO va aquí
- Secretos / claves (van en variables de entorno, nunca en el repo).
- Documentación de arquitectura (vive en Confluence, ver arriba).
