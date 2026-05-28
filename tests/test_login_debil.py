# TEST DEBIL (el que la IA escribe por defecto): solo confirma que algo pasa.
# No verifica la REGLA de negocio. Coverage alto, valor real bajo.
def test_login_devuelve_algo():
    resultado = {"ok": False, "error": "..."}
    assert resultado is not None          # no prueba nada util
    assert "ok" in resultado              # solo confirma la forma
