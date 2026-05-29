"""Inicio de sesión con correo y contraseña (HU-001).

Reglas (ver src/auth/CLAUDE.md):
- Las contraseñas se cifran con bcrypt; nunca se comparan ni guardan en texto plano.
- Tras 5 intentos fallidos, la cuenta se bloquea 15 minutos.
- El mensaje de error nunca revela si falló el correo o la contraseña.
- Cada intento (éxito o fallo) se registra SIN incluir la contraseña.
- Si el servicio de autenticación no responde, se devuelve un mensaje claro
  en vez de propagar la excepción.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional, Protocol

import bcrypt

logger = logging.getLogger("auth.login")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 15 * 60

# Mensaje único e indistinguible: no revela qué campo falló (criterio 4).
INVALID_CREDENTIALS_MESSAGE = "Correo o contrasena incorrectos."
ACCOUNT_LOCKED_MESSAGE = "Cuenta bloqueada temporalmente. Intenta de nuevo mas tarde."
SERVICE_UNAVAILABLE_MESSAGE = "Servicio no disponible. Intenta mas tarde."


class AuthServiceUnavailable(Exception):
    """El backend de autenticación no respondió."""


@dataclass
class User:
    """Usuario almacenado. `password_hash` es un hash bcrypt, nunca texto plano."""

    email: str
    password_hash: bytes
    failed_attempts: int = 0
    locked_until: Optional[float] = None


class UserDirectory(Protocol):
    """Origen de usuarios. Puede lanzar AuthServiceUnavailable si el backend cae."""

    def get_user(self, email: str) -> Optional[User]: ...

    def save_user(self, user: User) -> None: ...


@dataclass
class LoginResult:
    ok: bool
    message: Optional[str] = None
    locked: bool = False


def hash_password(plain_password: str) -> bytes:
    """Cifra una contraseña con bcrypt. Único punto que toca texto plano."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())


class LoginService:
    def __init__(self, directory: UserDirectory, *, clock=time.time) -> None:
        self._directory = directory
        self._clock = clock

    def login(self, email: str, password: str) -> LoginResult:
        # NUNCA registrar `password`. Solo el correo y el resultado.
        try:
            user = self._directory.get_user(email)
        except AuthServiceUnavailable:
            logger.warning("login_error_servicio email=%s", email)
            return LoginResult(ok=False, message=SERVICE_UNAVAILABLE_MESSAGE)

        now = self._clock()

        if user is not None and self._is_locked(user, now):
            logger.info("login_bloqueado email=%s", email)
            return LoginResult(ok=False, message=ACCOUNT_LOCKED_MESSAGE, locked=True)

        # Verificación en tiempo (cuasi) constante: comparamos siempre con bcrypt,
        # incluso si el usuario no existe, para no revelar qué campo falló.
        if user is None or not self._password_matches(password, user.password_hash):
            return self._register_failure(email, user, now)

        # Éxito: limpiar contador de fallos.
        user.failed_attempts = 0
        user.locked_until = None
        self._directory.save_user(user)
        logger.info("login_exitoso email=%s", email)
        return LoginResult(ok=True)

    def _is_locked(self, user: User, now: float) -> bool:
        return user.locked_until is not None and now < user.locked_until

    def _password_matches(self, password: str, password_hash: bytes) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)

    def _register_failure(
        self, email: str, user: Optional[User], now: float
    ) -> LoginResult:
        locked = False
        if user is not None:
            user.failed_attempts += 1
            if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = now + LOCKOUT_DURATION_SECONDS
                locked = True
            self._directory.save_user(user)

        logger.info("login_fallido email=%s bloqueado=%s", email, locked)
        if locked:
            return LoginResult(ok=False, message=ACCOUNT_LOCKED_MESSAGE, locked=True)
        return LoginResult(ok=False, message=INVALID_CREDENTIALS_MESSAGE)
