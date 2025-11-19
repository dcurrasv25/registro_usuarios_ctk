import csv
from pathlib import Path


class Usuario:
    def __init__(self, nombre: str, edad: int, genero: str = "", avatar: str = ""):
        self.nombre = nombre
        self.edad = int(edad) if edad is not None and edad != "" else None
        self.genero = genero
        self.avatar = avatar  # ruta relativa o absoluta a la imagen

    def to_tuple(self):
        return (self.nombre, str(self.edad) if self.edad is not None else "", self.genero, self.avatar)


class GestorUsuarios:
    def __init__(self, csv_path: Path = None):
        self._usuarios = []
        self.csv_path = Path(csv_path) if csv_path is not None else None
        self._cargar_datos_de_ejemplo()

    def _cargar_datos_de_ejemplo(self):
        # Añadir unos usuarios de ejemplo
        if not self._usuarios:
            self._usuarios.append(Usuario("Ejemplo Uno", 30, "M", ""))
            self._usuarios.append(Usuario("Ejemplo Dos", 25, "F", ""))

    def listar(self):
        return list(self._usuarios)

    def buscar_y_filtrar(self, nombre_filtro: str = "", genero_filtro: str = "Todos"):
        resultado = []
        for u in self._usuarios:
            nombre_match = nombre_filtro.lower() in u.nombre.lower()
            genero_match = genero_filtro == "Todos" or u.genero == genero_filtro
            if nombre_match and genero_match:
                resultado.append(u)
        return resultado

    def get_usuario(self, index: int):
        try:
            return self._usuarios[index]
        except Exception:
            return None

    def agregar_usuario(self, usuario: Usuario):
        if not usuario or not usuario.nombre:
            raise ValueError("Usuario inválido")
        self._usuarios.append(usuario)

    def actualizar_usuario(self, index: int, usuario: Usuario):
        if 0 <= index < len(self._usuarios):
            self._usuarios[index] = usuario

    def eliminar_usuario(self, index: int):
        if 0 <= index < len(self._usuarios):
            del self._usuarios[index]

    def guardar_csv(self, path: Path = None):
        path = Path(path) if path is not None else self.csv_path
        if path is None:
            raise ValueError("Ruta CSV no establecida")

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["nombre", "edad", "genero", "avatar"])
            for u in self._usuarios:
                writer.writerow(u.to_tuple())

    def cargar_csv(self, path: Path = None):
        path = Path(path) if path is not None else self.csv_path
        if path is None:
            raise ValueError("Ruta CSV no establecida")

        try:
            with path.open("r", newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                except StopIteration:
                    return
                self._usuarios.clear()
                for i, row in enumerate(reader):
                    try:
                        if not row:
                            continue
                        nombre = row[0]
                        edad = int(row[1]) if len(row) > 1 and row[1] != "" else None
                        genero = row[2] if len(row) > 2 else ""
                        avatar = row[3] if len(row) > 3 else ""
                        self._usuarios.append(Usuario(nombre, edad, genero, avatar))
                    except Exception:
                        # ignorar filas corruptas pero continuar
                        continue
        except FileNotFoundError:
            # No hay CSV aún; no es un error
            return
