import customtkinter as ctk
from componentes.tema import COLORES, FUENTES


class TarjetaEstadistica(ctk.CTkFrame):

    def __init__(self, master, titulo, valor, icono="📦", color_icono=None,
                 subtitulo=None, color_subtitulo=None):
        super().__init__(master, fg_color=COLORES["blanco"], corner_radius=12,
                         border_width=1, border_color=COLORES["borde"])
        color_icono = color_icono or COLORES["azul_activo"]
        color_subtitulo = color_subtitulo or COLORES["texto_claro"]

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=(18, 5))

        circulo = ctk.CTkFrame(fila, fg_color=COLORES["azul_claro"],
                               width=48, height=48, corner_radius=24)
        circulo.pack(side="left")
        circulo.pack_propagate(False)
        ctk.CTkLabel(circulo, text=icono, font=("Segoe UI", 22),
                     text_color=color_icono).pack(expand=True)

        ctk.CTkLabel(fila, text=titulo, font=FUENTES["texto"],
                     text_color=COLORES["texto_claro"]).pack(side="left", padx=12)

        ctk.CTkLabel(self, text=str(valor), font=FUENTES["stat"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20)

        if subtitulo:
            ctk.CTkLabel(self, text=subtitulo, font=FUENTES["texto_peq"],
                         text_color=color_subtitulo).pack(anchor="w", padx=20, pady=(0, 18))
        else:
            ctk.CTkFrame(self, fg_color="transparent", height=10).pack()