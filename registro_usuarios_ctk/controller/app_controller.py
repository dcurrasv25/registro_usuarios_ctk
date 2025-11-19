import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
import time

try:
    from PIL import Image
except ImportError:
    Image = None

from model.usuario_model import GestorUsuarios, Usuario
from view.main_view import MainView, AddUserView, EditUserView


class AppController:
    def __init__(self, master: ctk.CTk):
        self.master = master
        # Rutas base
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.ASSETS_PATH = self.BASE_DIR / "assets"
        self.CSV_PATH = self.BASE_DIR / "usuarios.csv"

        # Modelo y vista
        self.model = GestorUsuarios(self.CSV_PATH)
        self.view = MainView(master)

        # Caché de avatares para reutilizar imágenes
        self.avatar_cache = {}

        # Estado: índice seleccionado
        self._selected_index = None
        self._selected_usuario = None

        # Auto-guardado
        self._autosave_active = False
        self._autosave_thread = None
        self._autosave_stop_event = threading.Event()

        # Control de búsqueda y filtrado
        self._all_usuarios = []
        self._filtered_usuarios = []

        # Conectar botones de la vista a métodos del controlador
        self.view.btn_anadir.configure(command=self.abrir_ventana_anadir)
        self.view.btn_eliminar.configure(command=self.eliminar_usuario_seleccionado)
        self.view.btn_editar.configure(command=self.abrir_ventana_editar)
        self.view.btn_auto_guardar.configure(command=self.toggle_autosave)
        self.view.btn_buscar.configure(command=self.buscar_usuarios)

        # Conectar menú archivo
        self.view.menu_archivo.add_command(label="Guardar", command=self.guardar_usuarios)
        self.view.menu_archivo.add_command(label="Cargar", command=self.cargar_usuarios)
        self.view.menu_archivo.add_separator()
        self.view.menu_archivo.add_command(label="Salir", command=self.on_salir)

        # Inicializar lista desde modelo (carga automática)
        try:
            self.cargar_usuarios()
        finally:
            self.refrescar_lista_usuarios()

    def buscar_usuarios(self):
        """Busca y filtra usuarios por nombre y género"""
        nombre_filtro = self.view.search_var.get().lower()
        genero_filtro = self.view.genero_var.get()
        
        usuarios_filtrados = []
        for usuario in self.model.listar():
            nombre_match = nombre_filtro in usuario.nombre.lower()
            genero_match = genero_filtro == "Todos" or usuario.genero == genero_filtro
            if nombre_match and genero_match:
                usuarios_filtrados.append(usuario)
        
        # Mostrar resultado filtrado
        self._filtered_usuarios = usuarios_filtrados
        self.view.actualizar_lista_usuarios(
            usuarios_filtrados,
            self.seleccionar_usuario,
            self.abrir_ventana_editar_desde_doble_clic
        )
        self._limpiar_seleccion_si_fuera_de_lista(usuarios_filtrados)
        
        # Actualizar barra de estado
        total = len(self.model.listar())
        filtrados = len(usuarios_filtrados)
        if nombre_filtro or genero_filtro != "Todos":
            self.view.set_status(f"Búsqueda: {filtrados}/{total}")
        else:
            self.view.set_status(f"Usuarios: {filtrados}/{total}")

    def _on_search_or_filter_change(self):
        """Llamado cuando cambia la búsqueda o filtro"""
        nombre_filtro = self.view.search_var.get()
        genero_filtro = self.view.genero_var.get()
        self._filtered_usuarios = self.model.buscar_y_filtrar(nombre_filtro, genero_filtro)
        self.refrescar_lista_usuarios(filtrado=True)

    def refrescar_lista_usuarios(self, filtrado=False):
        """Refresca la lista mostrando usuarios filtrados o todos"""
        if filtrado:
            usuarios = self._filtered_usuarios
        else:
            usuarios = self.model.listar()
            self._all_usuarios = usuarios
            self._filtered_usuarios = usuarios

        self.view.actualizar_lista_usuarios(
            usuarios,
            self.seleccionar_usuario,
            self.abrir_ventana_editar_desde_doble_clic
        )
        self._limpiar_seleccion_si_fuera_de_lista(usuarios)
        
        # Actualizar barra de estado
        total = len(self.model.listar())
        filtrados = len(usuarios)
        self.view.set_status(f"Usuarios: {filtrados}/{total}")

    def seleccionar_usuario(self, usuario: Usuario):
        """Selecciona un usuario y muestra sus detalles"""
        if usuario is None:
            self._selected_usuario = None
            self._selected_index = None
            self.view.mostrar_detalles_usuario(None)
            return

        indice = self._obtener_indice_modelo(usuario)
        self._selected_usuario = usuario
        self._selected_index = indice

        avatar_image = None
        if usuario.avatar:
            avatar_image = self._cargar_avatar(usuario.avatar)

        self.view.mostrar_detalles_usuario(usuario, avatar_image)

    def _cargar_avatar(self, ruta_avatar: str):
        """Carga un avatar desde archivo (PNG, GIF, JPG)"""
        try:
            p = Path(ruta_avatar)
            if not p.is_absolute():
                p = (self.BASE_DIR / ruta_avatar).resolve()
            
            if not p.exists():
                return None
            
            cache_key = str(p)
            if cache_key in self.avatar_cache:
                return self.avatar_cache[cache_key]

            # Intentar con PIL y CTkImage para compatibilidad con más formatos
            if Image is not None:
                try:
                    pil_image = Image.open(p)
                    resampling_attr = getattr(Image, "Resampling", None)
                    if resampling_attr is not None:
                        pil_image.thumbnail((200, 200), resampling_attr.LANCZOS)
                    else:
                        pil_image.thumbnail((200, 200), Image.LANCZOS)
                    size = pil_image.size
                    ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
                    self.avatar_cache[cache_key] = ctk_image
                    return ctk_image
                except Exception:
                    pass

            # Fallback a PhotoImage si PIL no está disponible
            try:
                img = tk.PhotoImage(file=str(p))
                self.avatar_cache[cache_key] = img
                return img
            except Exception:
                return None
        except Exception:
            return None

    def abrir_ventana_anadir(self):
        """Abre la ventana para añadir un nuevo usuario"""
        add_view = AddUserView(self.master)
        add_view.guardar_button.configure(command=lambda: self.anadir_usuario(add_view))

    def anadir_usuario(self, add_view: AddUserView):
        """Añade un nuevo usuario"""
        data = add_view.get_data()
        nombre = data.get("nombre")
        edad_text = data.get("edad")
        genero = data.get("genero")
        avatar = data.get("avatar")

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        try:
            edad = int(edad_text) if edad_text != "" else None
        except ValueError:
            messagebox.showerror("Error", "Edad debe ser un número")
            return

        usuario = Usuario(nombre, edad, genero, avatar)
        try:
            self.model.agregar_usuario(usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {e}")
            return

        self.view.set_status(f"Usuario '{nombre}' añadido")
        self.refrescar_lista_usuarios()
        add_view.window.destroy()

    def abrir_ventana_editar(self):
        """Abre la ventana de edición para el usuario seleccionado"""
        if self._selected_usuario is None:
            messagebox.showinfo("Info", "Seleccione primero un usuario")
            return
        self._abrir_modal_edicion(self._selected_usuario)

    def abrir_ventana_editar_desde_doble_clic(self, usuario: Usuario):
        """Abre la ventana de edición (llamado desde doble clic o botón)"""
        if usuario is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        self._abrir_modal_edicion(usuario)

    def _abrir_modal_edicion(self, usuario: Usuario):
        indice = self._obtener_indice_modelo(usuario)
        if indice is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        edit_view = EditUserView(self.master, usuario)
        edit_view.guardar_button.configure(command=lambda: self.editar_usuario(indice, edit_view))

    def editar_usuario(self, indice: int, edit_view: EditUserView):
        """Edita un usuario existente"""
        data = edit_view.get_data()
        nombre = data.get("nombre")
        edad_text = data.get("edad")
        genero = data.get("genero")
        avatar = data.get("avatar")

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        try:
            edad = int(edad_text) if edad_text != "" else None
        except ValueError:
            messagebox.showerror("Error", "Edad debe ser un número")
            return

        usuario_actualizado = Usuario(nombre, edad, genero, avatar)
        try:
            self.model.actualizar_usuario(indice, usuario_actualizado)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar: {e}")
            return

        self.view.set_status(f"Usuario '{nombre}' actualizado")
        self.refrescar_lista_usuarios()
        usuario_refrescado = self.model.get_usuario(indice)
        if usuario_refrescado:
            self.seleccionar_usuario(usuario_refrescado)
        edit_view.window.destroy()

    def eliminar_usuario_seleccionado(self):
        """Elimina el usuario seleccionado"""
        if self._selected_index is None:
            messagebox.showinfo("Info", "Seleccione primero un usuario")
            return
        confirm = messagebox.askyesno("Confirmar", "Eliminar usuario seleccionado?")
        if not confirm:
            return
        try:
            self.model.eliminar_usuario(self._selected_index)
            self._selected_index = None
            self._selected_usuario = None
            self.view.set_status("Usuario eliminado")
            self.refrescar_lista_usuarios()
            self.view.mostrar_detalles_usuario(None)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def guardar_usuarios(self):
        """Guarda los usuarios en CSV"""
        try:
            self.model.guardar_csv(self.CSV_PATH)
            self.view.set_status(f"Guardado en {self.CSV_PATH.name}")
        except Exception as e:
            self.view.set_status(f"Error al guardar: {e}")
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def cargar_usuarios(self):
        """Carga los usuarios desde CSV"""
        try:
            self.model.cargar_csv(self.CSV_PATH)
            self.avatar_cache.clear()
            self._selected_index = None
            self._selected_usuario = None
            self.view.set_status("Datos cargados desde CSV")
        except Exception as e:
            self.view.set_status(f"Error al cargar: {e}")

    def toggle_autosave(self):
        """Activa/desactiva el auto-guardado"""
        if self._autosave_active:
            self._stop_autosave()
        else:
            self._start_autosave()

    def _start_autosave(self):
        """Inicia el auto-guardado en segundo plano"""
        self._autosave_active = True
        self.view.btn_auto_guardar.configure(text="Auto-guardar (ON)")
        self._autosave_stop_event.clear()
        self._autosave_thread = threading.Thread(target=self._autosave_worker, daemon=True)
        self._autosave_thread.start()
        self.view.set_status("Auto-guardado activado")

    def _stop_autosave(self):
        """Detiene el auto-guardado"""
        self._autosave_active = False
        self.view.btn_auto_guardar.configure(text="Auto-guardar (OFF)")
        self._autosave_stop_event.set()
        if self._autosave_thread:
            self._autosave_thread.join(timeout=1)
        self.view.set_status("Auto-guardado desactivado")

    def _autosave_worker(self):
        """Hilo de trabajo para auto-guardado cada 10 segundos"""
        while not self._autosave_stop_event.is_set():
            time.sleep(10)
            if not self._autosave_stop_event.is_set():
                # Usar after() para actualizar UI desde el hilo
                self.master.after(0, self._do_autosave)

    def _do_autosave(self):
        """Realiza el guardado automático"""
        try:
            self.model.guardar_csv(self.CSV_PATH)
            self.view.set_status("Auto-guardado: OK")
        except Exception as e:
            self.view.set_status(f"Auto-guardado: Error - {e}")

    def on_salir(self):
        """Maneja la salida de la aplicación"""
        self._stop_autosave()
        self.master.quit()

    def _obtener_indice_modelo(self, usuario: Usuario):
        if usuario is None:
            return None
        for idx, u in enumerate(self.model.listar()):
            if u is usuario:
                return idx
        return None

    def _limpiar_seleccion_si_fuera_de_lista(self, usuarios_visibles):
        if self._selected_usuario is None:
            return
        if self._selected_usuario not in usuarios_visibles:
            self._selected_usuario = None
            self._selected_index = None
            self.view.mostrar_detalles_usuario(None)
