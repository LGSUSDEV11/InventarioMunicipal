import sys
from conexion import ConexionPostgresql
from conexion import ConexionSqlServer
from vistas.login import VentanaLogin
from vistas.ventana_principal import VentanaPrincipal

def iniciar_sesion(usuario):
    # 1. Conectar a PostgreSQL
    cnn_pg = ConexionPostgresql()
    if cnn_pg.crear_conexion() is None:
        print("No se pudo conectar a PostgreSQL.")
        sys.exit(1)

    # 2. Conectar a SQL Server
    cnn_sql = ConexionSqlServer()
    if cnn_sql.crear_conexion() is None:
        print("No se pudo conectar a SQL Server. (Se usará PostgreSQL para todo).")
        # Nota: Si no hay SQL Server, la app igual abre, pero el módulo de usuarios fallará.

    # 3. Abrir la ventana principal y pasarle AMBAS conexiones
    app = VentanaPrincipal(cnn_pg, cnn_sql, usuario)
    app.mainloop()
    
    # 4. Cerrar conexiones al salir
    cnn_pg.cerrar_conexion()
    if cnn_sql.CNX:
        cnn_sql.cerrar_conexion()

if __name__ == "__main__":
    login = VentanaLogin(al_ingresar=iniciar_sesion)
    login.mainloop()