# Presencia de este archivo en la raíz hace que pytest agregue la raíz del repo
# a sys.path, para que `from src.auth.login import ...` funcione igual en local
# y en CI (sin depender de cómo se invoque pytest).
