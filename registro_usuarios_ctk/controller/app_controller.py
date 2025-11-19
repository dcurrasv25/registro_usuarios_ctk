from model.usuario_model import GestorUsuarios
from view.main_view import MainView


class AppController:
    def __init__(self, master):
        self.master = master
        self.model = GestorUsuarios()
        self.view = MainView(master)

        self.refrescar_lista_usuarios()

    def refrescar_lista_usuarios(self):
        usuarios = self.model.listar()
        self.view.actualizar_lista_usuarios(usuarios, self.seleccionar_usuario)
        self.view.mostrar_detalles_usuario(None)

    def seleccionar_usuario(self, indice: int):
        usuario = self.model.get_usuario(indice)
        self.view.mostrar_detalles_usuario(usuario)
