import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog


class MainView:
    def __init__(self, master):
        self.master = master

        self.left_frame = ctk.CTkFrame(master)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(master)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=2)

        self.lista_usuarios_scrollable = ctk.CTkScrollableFrame(self.left_frame, width=250)
        self.lista_usuarios_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

        self.btn_anadir = ctk.CTkButton(self.left_frame, text="Añadir Usuario")
        self.btn_anadir.pack(fill="x", padx=5, pady=(5, 0))

        self.avatar_label = ctk.CTkLabel(self.right_frame, text="[Sin Avatar]")
        self.avatar_label.pack(padx=10, pady=10)

        self.lbl_nombre = ctk.CTkLabel(self.right_frame, text="Nombre: ")
        self.lbl_nombre.pack(anchor="w", padx=10, pady=(5, 2))

        self.lbl_edad = ctk.CTkLabel(self.right_frame, text="Edad: ")
        self.lbl_edad.pack(anchor="w", padx=10, pady=(2, 2))

        self.lbl_genero = ctk.CTkLabel(self.right_frame, text="Género: ")
        self.lbl_genero.pack(anchor="w", padx=10, pady=(2, 2))

    def actualizar_lista_usuarios(self, usuarios, on_seleccionar_callback):
        for child in self.lista_usuarios_scrollable.winfo_children():
            child.destroy()

        for i, usuario in enumerate(usuarios):
            btn = ctk.CTkButton(
                self.lista_usuarios_scrollable,
                text=usuario.nombre,
                command=lambda idx=i: on_seleccionar_callback(idx),
            )
            btn.pack(fill="x", padx=5, pady=2)

    def mostrar_detalles_usuario(self, usuario, avatar_image=None):
        if usuario is None:
            self.lbl_nombre.configure(text="Nombre: ")
            self.lbl_edad.configure(text="Edad: ")
            self.lbl_genero.configure(text="Género: ")
            self.avatar_label.configure(text="[Sin Avatar]", image=None)
            self.avatar_label.image = None
            return

        self.lbl_nombre.configure(text=f"Nombre: {usuario.nombre}")
        self.lbl_edad.configure(text=f"Edad: {usuario.edad}")
        self.lbl_genero.configure(text=f"Género: {usuario.genero}")
        if avatar_image is not None:
            self.avatar_label.configure(image=avatar_image, text="")
            self.avatar_label.image = avatar_image
        else:
            self.avatar_label.configure(text="[Sin Avatar]", image=None)
            self.avatar_label.image = None


class AddUserView:
    def __init__(self, master):
        self.window = ctk.CTkToplevel(master)
        self.window.title("Añadir Nuevo Usuario")
        self.window.geometry("320x300")
        self.window.grab_set()

        self.nombre_entry = ctk.CTkEntry(self.window, placeholder_text="Nombre")
        self.nombre_entry.pack(fill="x", padx=10, pady=(10, 5))

        self.edad_entry = ctk.CTkEntry(self.window, placeholder_text="Edad")
        self.edad_entry.pack(fill="x", padx=10, pady=5)

        self.genero_var = tk.StringVar(value="M")
        self.genero_menu = ctk.CTkOptionMenu(self.window, values=["M", "F", "Otro"], variable=self.genero_var)
        self.genero_menu.pack(fill="x", padx=10, pady=5)

        self.avatar_path = None
        self.btn_seleccionar_avatar = ctk.CTkButton(self.window, text="Seleccionar Avatar", command=self._seleccionar_avatar)
        self.btn_seleccionar_avatar.pack(fill="x", padx=10, pady=5)

        self.guardar_button = ctk.CTkButton(self.window, text="Guardar")
        self.guardar_button.pack(side="bottom", fill="x", padx=10, pady=10)

    def _seleccionar_avatar(self):
        path = filedialog.askopenfilename(title="Seleccionar avatar", filetypes=[("Imágenes", "*.png;*.gif;*.ppm;*.pgm")])
        if path:
            self.avatar_path = path

    def get_data(self):
        return {
            "nombre": self.nombre_entry.get().strip(),
            "edad": self.edad_entry.get().strip(),
            "genero": self.genero_var.get(),
            "avatar": self.avatar_path or "",
        }
