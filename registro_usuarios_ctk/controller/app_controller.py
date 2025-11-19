from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from model.usuario_model import GestorUsuarios, Usuario
from view.main_view import MainView, AddUserView, EditUserView


class AppController:
    def __init__(self, master):
        self.master = master
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.CSV_PATH = self.BASE_DIR / "usuarios.csv"

        self.model = GestorUsuarios(self.CSV_PATH)
        self.view = MainView(master)

        self.avatar_cache = {}
        self._selected_index = None
        self._filtered_indices = []

        # Botones principales
        self.view.btn_anadir.configure(command=self.abrir_ventana_anadir)
        self.view.btn_editar.configure(command=self.abrir_ventana_editar)
        self.view.btn_eliminar.configure(command=self.eliminar_usuario)
        self.view.btn_buscar.configure(command=self.buscar_usuarios)

        # Menú archivo
        self.view.menu_archivo.add_command(label="Guardar", command=self.guardar_usuarios)
        self.view.menu_archivo.add_command(label="Cargar", command=self.cargar_usuarios)
        self.view.menu_archivo.add_separator()
        self.view.menu_archivo.add_command(label="Salir", command=self.master.destroy)

        # Callbacks de búsqueda
        self.view.search_var.trace_add("write", lambda *_: self.buscar_usuarios(auto=True))
        self.view.genero_var.trace_add("write", lambda *_: self.buscar_usuarios(auto=True))

        self.cargar_usuarios()

    def refrescar_lista_usuarios(self, indices=None):
        usuarios = self.model.listar()
        if indices is None:
            data = list(enumerate(usuarios))
        else:
            data = [(idx, usuarios[idx]) for idx in indices if 0 <= idx < len(usuarios)]
        self.view.actualizar_lista_usuarios(data, self.seleccionar_usuario, self.abrir_ventana_editar_indice)
        total = len(usuarios)
        visibles = len(data)
        self.view.set_status(f"Usuarios: {visibles}/{total}")

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
        self.view.set_status(f"Usuario '{nombre}' añadido")
        self.buscar_usuarios()
        add_view.window.destroy()

    def abrir_ventana_editar(self):
        if self._selected_index is None:
            messagebox.showinfo("Información", "Seleccione un usuario primero")
            return
        self.abrir_ventana_editar_indice(self._selected_index)

    def abrir_ventana_editar_indice(self, indice: int):
        usuario = self.model.get_usuario(indice)
        if usuario is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        edit_view = EditUserView(self.master, usuario)
        edit_view.guardar_button.configure(command=lambda: self.editar_usuario(indice, edit_view))

    def editar_usuario(self, indice: int, edit_view: EditUserView):
        data = edit_view.get_data()
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
        self.model.actualizar_usuario(indice, usuario)
        self.view.set_status(f"Usuario '{nombre}' actualizado")
        self.buscar_usuarios()
        edit_view.window.destroy()

    def eliminar_usuario(self):
        if self._selected_index is None:
            messagebox.showinfo("Información", "Seleccione un usuario primero")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar usuario seleccionado?"):
            return
        self.model.eliminar_usuario(self._selected_index)
        self._selected_index = None
        self.view.mostrar_detalles_usuario(None)
        self.view.set_status("Usuario eliminado")
        self.buscar_usuarios()

    def guardar_usuarios(self):
        try:
            self.model.guardar_csv(self.CSV_PATH)
            self.view.set_status(f"Guardado en {self.CSV_PATH.name}")
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
            self._selected_index = None
            self.buscar_usuarios()

    def buscar_usuarios(self, *_args, auto=False):
        nombre_filtro = self.view.search_var.get()
        genero = self.view.genero_var.get()

        coincidencias = self.model.buscar_y_filtrar(nombre_filtro, genero)
        self._filtered_indices = [idx for idx, _ in coincidencias]
        self.view.actualizar_lista_usuarios(coincidencias, self.seleccionar_usuario, self.abrir_ventana_editar_indice)

        total = len(self.model.listar())
        visibles = len(coincidencias)
        if nombre_filtro or genero != "Todos":
            self.view.set_status(f"Búsqueda: {visibles}/{total}")
        else:
            self.view.set_status(f"Usuarios: {visibles}/{total}")

        if self._selected_index is not None and self._selected_index not in self._filtered_indices:
            self._selected_index = None
            self.view.mostrar_detalles_usuario(None)
