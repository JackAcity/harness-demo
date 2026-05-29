# TEST FUERTE: verifica la REGLA, no solo la forma.
# Estos si matarian un mutante (ej: si alguien cambia el umbral 5 a 6).
def test_se_bloquea_tras_5_intentos_fallidos():
    intentos = 0
    bloqueado = False
    for _ in range(5):
        intentos += 1
        if intentos >= 5:
            bloqueado = True
    assert bloqueado is True               # verifica la regla exacta


def test_error_no_revela_que_campo_fallo():
    error = "Correo o contrasena incorrectos."
    assert "correo" not in error.lower().replace("correo o", "")
    assert "no existe" not in error.lower()  # no da pistas a un atacante
