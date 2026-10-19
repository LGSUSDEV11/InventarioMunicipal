import sys
from conexion import ConexionPostgresql
from vistas.login import VentanaLogin
from vistas.ventana_principal import VentanaPrincipal


def iniciar_sesion(usuario):
    cnn = ConexionPostgresql()
    if cnn.crear_conexion() is None:
        print("No se pudo conectar a la base de datos.")
        sys.exit(1)

    app = VentanaPrincipal(cnn, usuario)
    app.mainloop()
    cnn.cerrar_conexion()


if __name__ == "__main__":
    login = VentanaLogin(al_ingresar=iniciar_sesion)
    login.mainloop() 	 	 