import customtkinter as ctk
from componentes.tema import COLORES, FUENTES


class VentanaLogin(ctk.CTk):

    def __init__(self, al_ingresar):
        super().__init__()
        self.al_ingresar = al_ingresar

        self.title("Acceso — Sistema de Inventario Municipal")
        self.geometry("900x560")
        self.resizable(False, False)
        self.configure(fg_color=COLORES["fondo"])

        self._construir()

    def _construir(self):
        contenedor = ctk.CTkFrame(self, fg_color=COLORES["blanco"], corner_radius=16)
        contenedor.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.78)

        izquierda = ctk.CTkFrame(contenedor, fg_color=COLORES["azul_oscuro"], corner_radius=16)
        izquierda.place(relx=0, rely=0, relwidth=0.45, relheight=1)

        ctk.CTkLabel(izquierda, text="SAHUAYO", font=("Segoe UI", 28, "bold"),
                    text_color=COLORES["blanco"]).pack(pady=(70, 0))
        ctk.CTkLabel(izquierda, text="GOBIERNO", font=("Segoe UI", 14),
                    text_color=COLORES["texto_sidebar"]).pack()
        ctk.CTkLabel(izquierda, text="TODOS PODEMOS", font=("Segoe UI", 12),
                    text_color=COLORES["texto_sidebar"]).pack(pady=(0, 40))
        ctk.CTkLabel(izquierda,
                    text="Sistema de Inventario\nde Bienes Patrimoniales",
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORES["blanco"], justify="center").pack(pady=20)

        derecha = ctk.CTkFrame(contenedor, fg_color=COLORES["blanco"], corner_radius=16)
        derecha.place(relx=0.45, rely=0, relwidth=0.55, relheight=1)

        ctk.CTkLabel(derecha, text="Iniciar sesión",
                    font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(pady=(70, 5))
        ctk.CTkLabel(derecha, text="Ingrese sus credenciales para continuar",
                    font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(pady=(0, 30))

        self.entry_usuario = ctk.CTkEntry(
            derecha, placeholder_text="Usuario", width=320, height=42,
            font=FUENTES["texto"], corner_radius=8,
            border_color=COLORES["borde"]
        )
        self.entry_usuario.pack(pady=8)

        self.entry_password = ctk.CTkEntry(
            derecha, placeholder_text="Contraseña", show="●", width=320, height=42,
            font=FUENTES["texto"], corner_radius=8,
            border_color=COLORES["borde"]
        )
        self.entry_password.pack(pady=8)

        self.entry_usuario.insert(0, "admin.tesoreria")
        self.entry_password.insert(0, "1234")

        ctk.CTkButton(
            derecha, text="Ingresar", width=320, height=44,
            font=FUENTES["boton"], corner_radius=8,
            fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
            command=self._ingresar
        ).pack(pady=(20, 10))

        ctk.CTkLabel(derecha, text="© 2025 H. Ayuntamiento de Sahuayo",
                    font=FUENTES["texto_peq"],
                    text_color=COLORES["texto_claro"]).pack(side="bottom", pady=20)

    def _ingresar(self):
        usuario = self.entry_usuario.get().strip()
        if not usuario:
            return
        self.destroy()
        self.al_ingresar(usuario)