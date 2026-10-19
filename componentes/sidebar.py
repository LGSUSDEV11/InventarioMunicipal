import customtkinter as ctk
from componentes.tema import COLORES, FUENTES


class Sidebar(ctk.CTkFrame):

    ITEMS = [
        ("Inicio", "🏠", "inicio"),
        ("Consulta de bienes", "🔍", "consulta"),
        ("Alta de bienes", "➕", "alta"),
        ("Movimientos", "🔄", "movimientos"),
        ("Conciliación", "📋", "conciliacion"),
        ("Reportes", "📊", "reportes"),
        ("Usuarios", "👥", "usuarios"),
        ("Configuración", "⚙️", "configuracion"),
    ]

    def __init__(self, master, al_seleccionar):
        super().__init__(master, fg_color=COLORES["azul_oscuro"], corner_radius=0, width=240)
        self.pack_propagate(False)
        self.al_seleccionar = al_seleccionar
        self.botones = {}
        self.activo = None

        titulo = ctk.CTkLabel(
            self, text="SAHUAYO\nGOBIERNO\nTODOS PODEMOS",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORES["blanco"], justify="left"
        )
        titulo.pack(anchor="w", padx=20, pady=(25, 30))

        for nombre, icono, clave in self.ITEMS:
            btn = ctk.CTkButton(
                self,
                text=f"  {icono}   {nombre}",
                font=FUENTES["texto"],
                fg_color="transparent",
                hover_color=COLORES["azul_hover"],
                text_color=COLORES["texto_sidebar"],
                anchor="w",
                height=42,
                corner_radius=8,
                command=lambda c=clave: self._click(c)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.botones[clave] = btn

    def _click(self, clave):
        self.marcar_activo(clave)
        self.al_seleccionar(clave)

    def marcar_activo(self, clave):
        for c, btn in self.botones.items():
            if c == clave:
                btn.configure(fg_color=COLORES["azul_activo"], text_color=COLORES["blanco"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORES["texto_sidebar"])
        self.activo = clave