"""Tests de la HU-001. Verifican las REGLAS, no solo la forma.

Cubren los 4 criterios de aceptación y los no funcionales del issue #1.
"""

import logging

import pytest

from src.auth.login import (
    ACCOUNT_LOCKED_MESSAGE,
    AuthServiceUnavailable,
    INVALID_CREDENTIALS_MESSAGE,
    LOCKOUT_DURATION_SECONDS,
    MAX_FAILED_ATTEMPTS,
    SERVICE_UNAVAILABLE_MESSAGE,
    LoginService,
    User,
    hash_password,
)


class FakeDirectory:
    def __init__(self, users=None, *, raise_unavailable=False):
        self._users = {u.email: u for u in (users or [])}
        self._raise = raise_unavailable

    def get_user(self, email):
        if self._raise:
            raise AuthServiceUnavailable()
        return self._users.get(email)

    def save_user(self, user):
        self._users[user.email] = user


class FakeClock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now


def make_service(password="correcta", *, raise_unavailable=False):
    user = User(email="ana@empresa.com", password_hash=hash_password(password))
    clock = FakeClock()
    directory = FakeDirectory([user], raise_unavailable=raise_unavailable)
    return LoginService(directory, clock=clock), user, clock


# --- Criterio 1: credenciales correctas → entra ---
def test_credenciales_correctas_inician_sesion():
    service, _, _ = make_service(password="correcta")
    result = service.login("ana@empresa.com", "correcta")
    assert result.ok is True
    assert result.message is None


# --- Criterio 2: credenciales incorrectas → error, no entra ---
def test_password_incorrecta_no_inicia_sesion():
    service, _, _ = make_service(password="correcta")
    result = service.login("ana@empresa.com", "mala")
    assert result.ok is False


def test_correo_inexistente_no_inicia_sesion():
    service, _, _ = make_service()
    result = service.login("nadie@empresa.com", "lo-que-sea")
    assert result.ok is False


# --- Criterio 3: tras 5 intentos fallidos → bloqueo 15 min ---
def test_se_bloquea_exactamente_al_quinto_intento():
    service, user, _ = make_service(password="correcta")
    for _ in range(MAX_FAILED_ATTEMPTS - 1):
        r = service.login("ana@empresa.com", "mala")
        assert r.locked is False  # aún no bloqueada antes del 5º (mata mutante 5→6)
    r = service.login("ana@empresa.com", "mala")
    assert r.locked is True
    assert r.message == ACCOUNT_LOCKED_MESSAGE


def test_bloqueo_dura_15_minutos():
    service, _, clock = make_service(password="correcta")
    for _ in range(MAX_FAILED_ATTEMPTS):
        service.login("ana@empresa.com", "mala")
    # Aún dentro de los 15 min: sigue bloqueada incluso con clave correcta.
    clock.now += LOCKOUT_DURATION_SECONDS - 1
    assert service.login("ana@empresa.com", "correcta").locked is True
    # Pasados los 15 min: la clave correcta entra.
    clock.now += 2
    assert service.login("ana@empresa.com", "correcta").ok is True


# --- Criterio 4: el error no revela qué campo falló ---
def test_error_identico_para_correo_o_password_malos():
    service, _, _ = make_service(password="correcta")
    err_password = service.login("ana@empresa.com", "mala").message
    err_correo = service.login("nadie@empresa.com", "mala").message
    assert err_password == err_correo == INVALID_CREDENTIALS_MESSAGE
    assert "no existe" not in err_correo.lower()


# --- No funcional: contraseña nunca en texto plano ---
def test_password_se_almacena_cifrada_con_bcrypt():
    user = User(email="ana@empresa.com", password_hash=hash_password("secreta"))
    assert user.password_hash != b"secreta"
    assert user.password_hash.startswith(b"$2")  # prefijo bcrypt


# --- No funcional: cada intento se registra SIN la contraseña ---
def test_intentos_se_registran_sin_la_password(caplog):
    service, _, _ = make_service(password="correcta")
    with caplog.at_level(logging.INFO, logger="auth.login"):
        service.login("ana@empresa.com", "correcta")
        service.login("ana@empresa.com", "super-secreta-123")
    texto = caplog.text
    assert "login_exitoso" in texto
    assert "login_fallido" in texto
    assert "super-secreta-123" not in texto  # la password jamás se loguea
    assert "correcta" not in texto


# --- No funcional: servicio caído → mensaje claro, no excepción ---
def test_servicio_caido_devuelve_mensaje_y_no_propaga():
    service, _, _ = make_service(raise_unavailable=True)
    result = service.login("ana@empresa.com", "correcta")
    assert result.ok is False
    assert result.message == SERVICE_UNAVAILABLE_MESSAGE
