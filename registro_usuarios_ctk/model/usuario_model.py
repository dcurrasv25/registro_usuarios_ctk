import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Usuario:
    nombre: str
    edad: int
    genero: str
    avatar: str = ""


class GestorUsuarios:
    def __init__(self, csv_path: Path | None = None):
        self._usuarios = []
        self.csv_path = Path(csv_path) if csv_path else None
        self._cargar_datos_de_ejemplo()

    def _cargar_datos_de_ejemplo(self):
        if not self._usuarios:
            self._usuarios = [
                Usuario("Ejemplo Uno", 30, "M", "assets/avatar1.png"),
                Usuario("Ejemplo Dos", 25, "F", "assets/avatar2.png"),
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

    def actualizar_usuario(self, indice: int, usuario: Usuario):
        if not (0 <= indice < len(self._usuarios)):
            raise IndexError("Usuario inexistente")
        self._usuarios[indice] = usuario

    def eliminar_usuario(self, indice: int):
        if not (0 <= indice < len(self._usuarios)):
            raise IndexError("Usuario inexistente")
        del self._usuarios[indice]

    def buscar_y_filtrar(self, nombre_filtro: str = "", genero: str = "Todos"):
        resultado = []
        nombre_filtro = (nombre_filtro or "").lower()
        for idx, usuario in enumerate(self._usuarios):
            coincide_nombre = nombre_filtro in usuario.nombre.lower()
            coincide_genero = genero == "Todos" or usuario.genero == genero
            if coincide_nombre and coincide_genero:
                resultado.append((idx, usuario))
        return resultado

    def guardar_csv(self, path: Path | None = None):
        destino = Path(path) if path else self.csv_path
        if destino is None:
            raise ValueError("Ruta CSV no establecida")

        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nombre", "edad", "genero", "avatar"])
            for usuario in self._usuarios:
                writer.writerow([usuario.nombre, usuario.edad, usuario.genero, usuario.avatar])

    def cargar_csv(self, path: Path | None = None):
        origen = Path(path) if path else self.csv_path
        if origen is None:
            raise ValueError("Ruta CSV no establecida")

        try:
            with origen.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                self._usuarios.clear()
                for row in reader:
                    if not row:
                        continue
                    nombre = row[0]
                    edad = int(row[1]) if row[1] else 0
                    genero = row[2] if len(row) > 2 else ""
                    avatar = row[3] if len(row) > 3 else ""
                    self._usuarios.append(Usuario(nombre, edad, genero, avatar))
        except FileNotFoundError:
            # No existe todavía; mantener datos de ejemplo
            return
