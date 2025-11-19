import customtkinter as ctk

from controller.app_controller import AppController


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Registro de Usuarios (CTk + MVC)")
    app.geometry("900x600")

    controller = AppController(app)
    app.mainloop()
