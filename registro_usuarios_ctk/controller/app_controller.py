from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from model.usuario_model import GestorUsuarios, Usuario
from view.main_view import MainView, AddUserView


class AppController:
    def __init__(self, master):
        self.master = master
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.CSV_PATH = self.BASE_DIR / "usuarios.csv"

        self.model = GestorUsuarios(self.CSV_PATH)
        self.view = MainView(master)

        self.avatar_cache = {}
        self._selected_index = None

        self.view.btn_anadir.configure(command=self.abrir_ventana_anadir)
        self.view.menu_archivo.add_command(label="Guardar", command=self.guardar_usuarios)
        self.view.menu_archivo.add_command(label="Cargar", command=self.cargar_usuarios)
        self.view.menu_archivo.add_separator()
        self.view.menu_archivo.add_command(label="Salir", command=self.master.destroy)

        self.cargar_usuarios()

    def refrescar_lista_usuarios(self):
        usuarios = self.model.listar()
        self.view.actualizar_lista_usuarios(usuarios, self.seleccionar_usuario)
        self.view.mostrar_detalles_usuario(None)

    def seleccionar_usuario(self, indice: int):
        usuario = self.model.get_usuario(indice)
        self._selected_index = indice
        avatar_image = None
        if usuario and usuario.avatar:
            avatar_image = self._cargar_avatar(usuario.avatar)
        self.view.mostrar_detalles_usuario(usuario, avatar_image)

    def _cargar_avatar(self, ruta_avatar: str):
        try:
            path = Path(ruta_avatar)
            if not path.is_absolute():
                path = (self.BASE_DIR / ruta_avatar).resolve()

            if not path.exists():
                return None

            cache_key = str(path)
            if cache_key in self.avatar_cache:
                return self.avatar_cache[cache_key]

            image = tk.PhotoImage(file=str(path))
            self.avatar_cache[cache_key] = image
            return image
        except Exception:
            return None

    def abrir_ventana_anadir(self):
        add_view = AddUserView(self.master)
        add_view.guardar_button.configure(command=lambda: self.anadir_usuario(add_view))

    def anadir_usuario(self, add_view: AddUserView):
        data = add_view.get_data()
        nombre = data.get("nombre")
        edad_text = data.get("edad")
        genero = data.get("genero")
        avatar = data.get("avatar")

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        try:
            edad = int(edad_text) if edad_text else 0
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número")
            return

        usuario = Usuario(nombre, edad, genero, avatar)
        self.model.agregar_usuario(usuario)
        self.refrescar_lista_usuarios()
        add_view.window.destroy()

    def guardar_usuarios(self):
        try:
            self.model.guardar_csv(self.CSV_PATH)
            messagebox.showinfo("Guardar", "Usuarios guardados correctamente")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo guardar: {exc}")

    def cargar_usuarios(self):
        try:
            self.model.cargar_csv(self.CSV_PATH)
            self.avatar_cache.clear()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo cargar: {exc}")
        finally:
            self.refrescar_lista_usuarios()
