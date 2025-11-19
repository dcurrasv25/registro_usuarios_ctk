import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog


class MainView:
    def __init__(self, master):
        self.master = master
        # Menú (expuesto para conectar comandos desde el controlador)
        self.menubar = tk.Menu(master)
        master.config(menu=self.menubar)
        self.menu_archivo = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Archivo", menu=self.menu_archivo)

        # Barra de estado en la parte inferior
        self.status_frame = ctk.CTkFrame(master, height=30)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.status_label = ctk.CTkLabel(self.status_frame, text="Listo", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=5)

        # Layout principal: dos columnas
        self.left_frame = ctk.CTkFrame(master)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(master)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=2)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)

        # Búsqueda y filtro en la parte superior izquierda
        self.search_frame = ctk.CTkFrame(self.left_frame)
        self.search_frame.pack(fill="x", padx=5, pady=(0,5))

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Buscar por nombre")
        self.search_entry.pack(fill="x", pady=(0,3))

        self.genero_var = tk.StringVar(value="Todos")
        self.genero_menu = ctk.CTkOptionMenu(self.search_frame, values=["Todos", "M", "F", "Otro"], variable=self.genero_var)
        self.genero_menu.pack(fill="x")

        self.btn_buscar = ctk.CTkButton(self.search_frame, text="Buscar")
        self.btn_buscar.pack(fill="x", pady=(3,0))

        # Scrollable frame para la lista de usuarios
        self.lista_usuarios_scrollable = ctk.CTkScrollableFrame(self.left_frame, width=250)
        self.lista_usuarios_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones bajo la lista
        self.btn_anadir = ctk.CTkButton(self.left_frame, text="Añadir Usuario")
        self.btn_anadir.pack(fill="x", padx=5, pady=(5,2))

        self.btn_eliminar = ctk.CTkButton(self.left_frame, text="Eliminar Usuario")
        self.btn_eliminar.pack(fill="x", padx=5, pady=(2,2))

        self.btn_auto_guardar = ctk.CTkButton(self.left_frame, text="Auto-guardar (OFF)")
        self.btn_auto_guardar.pack(fill="x", padx=5, pady=(2,5))

        # Detalles a la derecha
        self.avatar_label = ctk.CTkLabel(self.right_frame, text="[Sin Avatar]")
        self.avatar_label.pack(padx=10, pady=10)

        self.lbl_nombre = ctk.CTkLabel(self.right_frame, text="Nombre: ")
        self.lbl_nombre.pack(anchor="w", padx=10, pady=(5,2))

        self.lbl_edad = ctk.CTkLabel(self.right_frame, text="Edad: ")
        self.lbl_edad.pack(anchor="w", padx=10, pady=(2,2))

        self.lbl_genero = ctk.CTkLabel(self.right_frame, text="Género: ")
        self.lbl_genero.pack(anchor="w", padx=10, pady=(2,2))

        self.btn_editar = ctk.CTkButton(self.right_frame, text="Editar Usuario")
        self.btn_editar.pack(fill="x", padx=10, pady=(20,2))

    def set_status(self, message: str):
        self.status_label.configure(text=message)

    def actualizar_lista_usuarios(self, usuarios, on_seleccionar_callback, on_editar_callback):
        # limpiar anteriores
        for child in self.lista_usuarios_scrollable.winfo_children():
            child.destroy()

        for usuario in usuarios:
            btn = ctk.CTkButton(
                self.lista_usuarios_scrollable,
                text=usuario.nombre,
                command=lambda user=usuario: on_seleccionar_callback(user)
            )
            # Doble clic para editar
            btn.bind("<Double-1>", lambda e, user=usuario: on_editar_callback(user))
            btn.pack(fill="x", padx=5, pady=2)

    def mostrar_detalles_usuario(self, usuario, avatar_image=None):
        if usuario is None:
            self.lbl_nombre.configure(text="Nombre: ")
            self.lbl_edad.configure(text="Edad: ")
            self.lbl_genero.configure(text="Género: ")
            self.avatar_label.configure(image=None, text="[Sin Avatar]")
            self.avatar_label.image = None
            return

        self.lbl_nombre.configure(text=f"Nombre: {usuario.nombre}")
        self.lbl_edad.configure(text=f"Edad: {usuario.edad}")
        self.lbl_genero.configure(text=f"Género: {usuario.genero}")
        if avatar_image:
            # avatar_image must be a tkinter.PhotoImage
            self.avatar_label.configure(image=avatar_image, text="")
            # keep reference to avoid GC (store on widget)
            self.avatar_label.image = avatar_image
        else:
            self.avatar_label.configure(image=None, text="[Sin Avatar]")
            self.avatar_label.image = None


class AddUserView:
    def __init__(self, master):
        self.window = ctk.CTkToplevel(master)
        self.window.title("Añadir Nuevo Usuario")
        self.window.geometry("320x300")
        self.window.grab_set()

        self.nombre_entry = ctk.CTkEntry(self.window, placeholder_text="Nombre")
        self.nombre_entry.pack(fill="x", padx=10, pady=(10,5))

        self.edad_entry = ctk.CTkEntry(self.window, placeholder_text="Edad")
        self.edad_entry.pack(fill="x", padx=10, pady=5)

        self.genero_var = tk.StringVar(value="Otro")
        self.genero_menu = ctk.CTkOptionMenu(self.window, values=["M","F","Otro"], variable=self.genero_var)
        self.genero_menu.pack(fill="x", padx=10, pady=5)

        self.avatar_path = None
        self.btn_seleccionar_avatar = ctk.CTkButton(self.window, text="Seleccionar Avatar", command=self._seleccionar_avatar)
        self.btn_seleccionar_avatar.pack(fill="x", padx=10, pady=5)

        self.guardar_button = ctk.CTkButton(self.window, text="Guardar")
        self.guardar_button.pack(side="bottom", fill="x", padx=10, pady=10)

    def _seleccionar_avatar(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Seleccionar avatar", filetypes=[("Images","*.png;*.gif;*.ppm;*.pgm")])
        if path:
            self.avatar_path = path

    def get_data(self):
        return {
            "nombre": self.nombre_entry.get().strip(),
            "edad": self.edad_entry.get().strip(),
            "genero": self.genero_var.get(),
            "avatar": self.avatar_path or ""
        }


class EditUserView:
    def __init__(self, master, usuario):
        self.window = ctk.CTkToplevel(master)
        self.window.title("Editar Usuario")
        self.window.geometry("320x300")
        self.window.grab_set()

        self.nombre_entry = ctk.CTkEntry(self.window, placeholder_text="Nombre")
        self.nombre_entry.insert(0, usuario.nombre)
        self.nombre_entry.pack(fill="x", padx=10, pady=(10,5))

        self.edad_entry = ctk.CTkEntry(self.window, placeholder_text="Edad")
        if usuario.edad is not None:
            self.edad_entry.insert(0, str(usuario.edad))
        self.edad_entry.pack(fill="x", padx=10, pady=5)

        self.genero_var = tk.StringVar(value=usuario.genero if usuario.genero else "Otro")
        self.genero_menu = ctk.CTkOptionMenu(self.window, values=["M","F","Otro"], variable=self.genero_var)
        self.genero_menu.pack(fill="x", padx=10, pady=5)

        self.avatar_path = usuario.avatar
        self.btn_seleccionar_avatar = ctk.CTkButton(self.window, text="Seleccionar Avatar", command=self._seleccionar_avatar)
        self.btn_seleccionar_avatar.pack(fill="x", padx=10, pady=5)

        self.guardar_button = ctk.CTkButton(self.window, text="Guardar")
        self.guardar_button.pack(side="bottom", fill="x", padx=10, pady=10)

    def _seleccionar_avatar(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Seleccionar avatar", filetypes=[("Images","*.png;*.gif;*.ppm;*.pgm")])
        if path:
            self.avatar_path = path

    def get_data(self):
        return {
            "nombre": self.nombre_entry.get().strip(),
            "edad": self.edad_entry.get().strip(),
            "genero": self.genero_var.get(),
            "avatar": self.avatar_path or ""
        }
