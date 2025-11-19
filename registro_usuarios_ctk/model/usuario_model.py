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
            Usuario("Ejemplo Uno", 30, "M"),
            Usuario("Ejemplo Dos", 25, "F"),
            Usuario("Ejemplo Tres", 28, "Otro"),
        ]

    def listar(self):
        return list(self._usuarios)

    def get_usuario(self, indice: int):
        if 0 <= indice < len(self._usuarios):
            return self._usuarios[indice]
        return None
