# Reglas del módulo de autenticación (aplican solo a src/auth/)

- Las contraseñas se cifran con bcrypt. Nunca se comparan ni se guardan en texto plano.
- Tras 5 intentos fallidos, la cuenta se bloquea 15 minutos.
- El mensaje de error nunca revela si falló el correo o la contraseña.
- Cada intento de login se registra (éxito o fallo) SIN incluir la contraseña.
