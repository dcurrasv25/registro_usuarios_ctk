from dataclasses import dataclass


@dataclass
class Usuario:
    nombre: str
    edad: int
    genero: str
    avatar: str = ""


class GestorUsuarios:
    def __init__(self):
        self._usuarios = []
        self._cargar_datos_de_ejemplo()

    def _cargar_datos_de_ejemplo(self):
        self._usuarios = [
            Usuario("Ejemplo Uno", 30, "M", "assets/avatar1.png"),
            Usuario("Ejemplo Dos", 25, "F", "assets/avatar2.png"),
            Usuario("Ejemplo Tres", 28, "Otro", ""),
        ]

    def listar(self):
        return list(self._usuarios)

    def get_usuario(self, indice: int):
        if 0 <= indice < len(self._usuarios):
            return self._usuarios[indice]
        return None

    def agregar_usuario(self, usuario: Usuario):
        if not usuario or not usuario.nombre:
            raise ValueError("Usuario inválido")
        self._usuarios.append(usuario)
