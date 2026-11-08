import customtkinter as ctk
from componentes.tema import COLORES
from componentes.sidebar import Sidebar
from componentes.topbar import Topbar
from vistas.inicio import VistaInicio


class VentanaPrincipal(ctk.CTk):

    def __init__(self, cnn_pg, cnn_sql, usuario):
        super().__init__()
        self.cnn_pg = cnn_pg    # Conexión a PostgreSQL (Clever Cloud)
        self.cnn_sql = cnn_sql  # Conexión a SQL Server (Local)
        self.usuario = usuario

        self.title("Sistema de Inventario de Bienes Patrimoniales — Sahuayo")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(fg_color=COLORES["fondo"])

        self._construir()
        self.mostrar("inicio")
        
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)
        
    def _al_cerrar(self):
        if self.cnn_pg:
            self.cnn_pg.cerrar_conexion()
        if self.cnn_sql and self.cnn_sql.CNX:
            self.cnn_sql.cerrar_conexion()
        self.destroy()


    def _construir(self):
        self.sidebar = Sidebar(self, al_seleccionar=self.mostrar)
        self.sidebar.pack(side="left", fill="y")

        contenedor_der = ctk.CTkFrame(self, fg_color=COLORES["fondo"], corner_radius=0)
        contenedor_der.pack(side="right", fill="both", expand=True)

        self.topbar = Topbar(contenedor_der, nombre_usuario=self.usuario)
        self.topbar.pack(fill="x")

        self.area = ctk.CTkFrame(contenedor_der, fg_color=COLORES["fondo"], corner_radius=0)
        self.area.pack(fill="both", expand=True)

        from vistas.consulta_bienes import VistaConsultaBienes
        from vistas.alta_bienes import VistaAltaBienes
        from vistas.movimientos import VistaMovimientos
        from vistas.conciliacion import VistaConciliacion
        from vistas.reportes import VistaReportes
        from vistas.usuarios import VistaUsuarios
        from vistas.configuracion import VistaConfiguracion

        self.vistas = {
            "inicio": lambda: VistaInicio(self.area, self.cnn_sql),     
            "consulta": lambda: VistaConsultaBienes(self.area, self.cnn_pg),
            "alta": lambda: VistaAltaBienes(self.area, self.cnn_pg),
            "movimientos": lambda: VistaMovimientos(self.area, self.cnn_pg),
            "conciliacion": lambda: VistaConciliacion(self.area, self.cnn_pg),
            "reportes": lambda: VistaReportes(self.area, self.cnn_pg),
            "usuarios": lambda: VistaUsuarios(self.area, self.cnn_pg),  
            "configuracion": lambda: VistaConfiguracion(self.area, self.cnn_pg),
        }

        pie = ctk.CTkLabel(
            contenedor_der,
            text="© 2025 H. Ayuntamiento de Sahuayo  |  Sistema de Inventario de Bienes Patrimoniales  |  Versión 1.0",
            font=("Segoe UI", 10), text_color=COLORES["texto_claro"]
        )
        pie.pack(fill="x", pady=6)

    def mostrar(self, clave):
        for w in self.area.winfo_children():
            w.destroy()

        constructor = self.vistas.get(clave)
        if constructor:
            vista = constructor()
            vista.pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(
                self.area,
                text=f"Módulo '{clave}' en construcción",
                font=("Segoe UI", 18), text_color=COLORES["texto_claro"]
            ).pack(expand=True)