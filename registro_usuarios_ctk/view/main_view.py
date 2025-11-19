import customtkinter as ctk


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

    def mostrar_detalles_usuario(self, usuario):
        if usuario is None:
            self.lbl_nombre.configure(text="Nombre: ")
            self.lbl_edad.configure(text="Edad: ")
            self.lbl_genero.configure(text="Género: ")
            self.avatar_label.configure(text="[Sin Avatar]")
            return

        self.lbl_nombre.configure(text=f"Nombre: {usuario.nombre}")
        self.lbl_edad.configure(text=f"Edad: {usuario.edad}")
        self.lbl_genero.configure(text=f"Género: {usuario.genero}")
        self.avatar_label.configure(text="[Sin Avatar]")
