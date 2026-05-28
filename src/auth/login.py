# =============================================================================
# EJEMPLO DE SALIDA ESPERADA (referencia para tus diapos).
# Para una captura AUTENTICA: borra este archivo y pidele a Claude Code:
#   "Implementa la funcion de login en src/auth/login.py segun las reglas del modulo."
# Claude leera src/auth/CLAUDE.md y generara codigo asi, SIN que se lo pidas
# explicitamente en el prompt (bcrypt, bloqueo por intentos, log sin password).
# =============================================================================
import logging
import bcrypt

logger = logging.getLogger("auth")

MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 15


def iniciar_sesion(correo, contrasena, repo_usuarios):
    """
    Inicia sesion. Cumple las reglas del modulo (src/auth/CLAUDE.md):
    - bcrypt, nunca texto plano
    - bloqueo tras 5 intentos
    - error generico (no revela que campo fallo)
    - registra el intento SIN la contrasena
    """
    usuario = repo_usuarios.buscar_por_correo(correo)

    if usuario and usuario.esta_bloqueado():
        logger.warning("Intento sobre cuenta bloqueada correo=%s", correo)  # sin password
        return _error_generico()

    # Comparacion con hash; la contrasena nunca se guarda en texto plano
    if usuario and bcrypt.checkpw(contrasena.encode(), usuario.hash_contrasena):
        usuario.reiniciar_intentos()
        logger.info("Login exitoso correo=%s", correo)  # sin password
        return {"ok": True, "panel": usuario.panel()}

    if usuario:
        usuario.sumar_intento_fallido()
        if usuario.intentos_fallidos >= MAX_INTENTOS:
            usuario.bloquear(BLOQUEO_MINUTOS)

    logger.info("Login fallido correo=%s", correo)  # sin password
    return _error_generico()


def _error_generico():
    # No revela si fallo el correo o la contrasena
    return {"ok": False, "error": "Correo o contrasena incorrectos."}
