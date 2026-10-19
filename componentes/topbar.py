import os
import customtkinter as ctk
from tkinter import PhotoImage
from componentes.tema import COLORES, FUENTES
from config import ASSETS_DIR


class Topbar(ctk.CTkFrame):

    def __init__(self, master, nombre_usuario="María López García", rol="Tesorera Municipal"):
        super().__init__(master, fg_color=COLORES["blanco"], height=70, corner_radius=0)
        self.pack_propagate(False)

        self._cargar_logo()

        ctk.CTkLabel(
            self, text="🔔", font=("Segoe UI", 20), text_color=COLORES["azul_oscuro"]
        ).pack(side="right", padx=(0, 20))

        ctk.CTkLabel(
            self, text="👤", font=("Segoe UI", 26), text_color=COLORES["azul_oscuro"]
        ).pack(side="right", padx=(0, 5))

        datos = ctk.CTkFrame(self, fg_color="transparent")
        datos.pack(side="right", padx=(0, 20))
        ctk.CTkLabel(datos, text=nombre_usuario, font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="e")
        ctk.CTkLabel(datos, text=rol, font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="e")

    def _cargar_logo(self):
        ruta_logo = os.path.join(ASSETS_DIR, "logo_sahuayo.png")
        if os.path.exists(ruta_logo):
            try:
                imagen = PhotoImage(file=ruta_logo)
                factor = max(1, imagen.width() // 180)
                imagen = imagen.subsample(factor, factor)
                lbl = ctk.CTkLabel(self, image=imagen, text="")
                lbl.image = imagen
                lbl.pack(side="left", padx=20)
                return
            except Exception:
                pass
        ctk.CTkLabel(
            self, text="SAHUAYO — GOBIERNO",
            font=("Segoe UI", 16, "bold"), text_color=COLORES["azul_oscuro"]
        ).pack(side="left", padx=20)