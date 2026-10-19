import customtkinter as ctk
from componentes.tema import COLORES, FUENTES


class Tabla(ctk.CTkFrame):

    def __init__(self, master, columnas, anchos=None):
        super().__init__(master, fg_color=COLORES["blanco"], corner_radius=12,
                         border_width=1, border_color=COLORES["borde"])
        self.columnas = columnas
        self.anchos = anchos or [1] * len(columnas)

        encabezado = ctk.CTkFrame(self, fg_color=COLORES["azul_claro"], corner_radius=0)
        encabezado.pack(fill="x")
        for i, col in enumerate(columnas):
            encabezado.grid_columnconfigure(i, weight=self.anchos[i])
            ctk.CTkLabel(encabezado, text=col, font=("Segoe UI", 11, "bold"),
                         text_color=COLORES["azul_oscuro"]).grid(
                row=0, column=i, sticky="w", padx=12, pady=10)

        self.cuerpo = ctk.CTkScrollableFrame(self, fg_color=COLORES["blanco"],
                                             corner_radius=0, height=280)
        self.cuerpo.pack(fill="both", expand=True)

    def cargar(self, filas):
        for w in self.cuerpo.winfo_children():
            w.destroy()

        for f_idx, fila in enumerate(filas):
            color_fondo = COLORES["blanco"] if f_idx % 2 == 0 else "#fafbfc"
            contenedor = ctk.CTkFrame(self.cuerpo, fg_color=color_fondo, corner_radius=0)
            contenedor.pack(fill="x")

            for i, valor in enumerate(fila):
                contenedor.grid_columnconfigure(i, weight=self.anchos[i])
                ctk.CTkLabel(contenedor, text=str(valor), font=FUENTES["texto_peq"],
                             text_color=COLORES["texto"], anchor="w").grid(
                    row=0, column=i, sticky="w", padx=12, pady=8)