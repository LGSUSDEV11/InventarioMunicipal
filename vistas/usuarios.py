import json
from datetime import datetime
from tkinter import messagebox
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES
from componentes.tabla import Tabla


class VistaUsuarios(ctk.CTkFrame):

    ROLES = ["Administrador", "Tesoreria", "Inventarios", "Contraloria", "Consulta"]
    ESTADOS = ["Activo", "Inactivo"]

    COLORES_ROL = {
        "Administrador": (COLORES["azul_claro"], COLORES["azul_activo"]),
        "Tesoreria": (COLORES["azul_claro"], COLORES["azul_boton"]),
        "Inventarios": (COLORES["morado_claro"], COLORES["morado"]),
        "Contraloria": (COLORES["amarillo_claro"], COLORES["amarillo"]),
        "Consulta": (COLORES["verde_claro"], COLORES["verde"]),
    }

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self.usuarios_actuales = []
        self.usuario_editando = None

        self._construir()
        self._buscar()

    def _construir(self):
        ctk.CTkLabel(self, text="👥  Usuarios", font=FUENTES["titulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Administración de cuentas de usuario y control de accesos al sistema.",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 15))

        fila_stats = ctk.CTkFrame(self, fg_color="transparent")
        fila_stats.pack(fill="x", padx=30, pady=(0, 15))
        for i in range(3):
            fila_stats.grid_columnconfigure(i, weight=1)

        self.tarjetas = {}
        defs = [
            ("total", "Total de usuarios", "👥", COLORES["azul_activo"], COLORES["azul_claro"]),
            ("activos", "Usuarios activos", "✅", COLORES["verde"], COLORES["verde_claro"]),
            ("inactivos", "Usuarios inactivos", "🛡️", COLORES["texto_claro"], COLORES["borde"]),
        ]
        for i, (clave, titulo, icono, color, bg) in enumerate(defs):
            t = self._tarjeta(fila_stats, titulo, icono, color, bg)
            t.grid(row=0, column=i, padx=8, sticky="nsew")
            self.tarjetas[clave] = t

        filtros = ctk.CTkFrame(self, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"])
        filtros.pack(fill="x", padx=30, pady=(0, 15))

        fila = ctk.CTkFrame(filtros, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=15)
        for i in range(4):
            fila.grid_columnconfigure(i, weight=1)

        self.entry_busqueda = ctk.CTkEntry(fila, placeholder_text="🔎  Buscar por nombre o usuario...",
                                             height=38, font=FUENTES["texto"], corner_radius=8)
        self.entry_busqueda.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(0, 10))

        self.combo_rol = self._combo(fila, "Rol", 2, ["Todos"] + self.ROLES)
        self.combo_estado = self._combo(fila, "Estado", 3, ["Todos"] + self.ESTADOS)

        botones = ctk.CTkFrame(filtros, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkButton(botones, text="Buscar", width=110, height=36, font=FUENTES["boton"],
                       corner_radius=8, fg_color=COLORES["azul_boton"],
                       hover_color=COLORES["azul_boton_hover"],
                       command=self._buscar).pack(side="left")
        ctk.CTkButton(botones, text="Limpiar", width=110, height=36, font=FUENTES["texto"],
                       corner_radius=8, fg_color=COLORES["borde"], hover_color="#d1d5db",
                       text_color=COLORES["texto"],
                       command=self._limpiar).pack(side="left", padx=10)

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        izquierda = ctk.CTkFrame(cuerpo, fg_color="transparent")
        izquierda.pack(side="left", fill="both", expand=True)

        self.lbl_contador = ctk.CTkLabel(izquierda, text="Mostrando 0 usuarios",
                                           font=FUENTES["texto_peq"],
                                           text_color=COLORES["texto_claro"])
        self.lbl_contador.pack(anchor="w", pady=(0, 5))

        self.contenedor_tabla = ctk.CTkFrame(izquierda, fg_color="transparent")
        self.contenedor_tabla.pack(fill="both", expand=True)

        derecha = ctk.CTkFrame(cuerpo, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"], width=340)
        derecha.pack(side="right", fill="y", padx=(20, 0))
        derecha.pack_propagate(False)

        self._panel_formulario(derecha)

    def _tarjeta(self, master, titulo, icono, color, color_bg):
        marco = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                              border_width=1, border_color=COLORES["borde"])
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=18, pady=(15, 5))

        circulo = ctk.CTkFrame(fila, fg_color=color_bg, width=44, height=44, corner_radius=22)
        circulo.pack(side="left")
        circulo.pack_propagate(False)
        ctk.CTkLabel(circulo, text=icono, font=("Segoe UI", 18), text_color=color).pack(expand=True)

        ctk.CTkLabel(fila, text=titulo, font=FUENTES["texto"],
                     text_color=COLORES["texto_claro"], wraplength=160, justify="left").pack(
            side="left", padx=10)

        valor = ctk.CTkLabel(marco, text="0", font=FUENTES["stat"], text_color=COLORES["texto"])
        valor.pack(anchor="w", padx=18, pady=(0, 15))
        marco.valor_widget = valor
        return marco

    def _combo(self, master, etiqueta, columna, opciones):
        cont = ctk.CTkFrame(master, fg_color="transparent")
        cont.grid(row=0, column=columna, padx=5, sticky="ew")
        ctk.CTkLabel(cont, text=etiqueta, font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w")
        combo = ctk.CTkComboBox(cont, values=opciones, height=38, font=FUENTES["texto"],
                                 corner_radius=8, state="readonly")
        combo.pack(fill="x", pady=(3, 0))
        combo.set(opciones[0])
        return combo

    def _panel_formulario(self, master):
        contenedor = ctk.CTkScrollableFrame(master, fg_color=COLORES["blanco"],
                                              corner_radius=0,
                                              scrollbar_button_color=COLORES["borde"])
        contenedor.pack(fill="both", expand=True)

        self.lbl_titulo_form = ctk.CTkLabel(contenedor, text="➕  Nuevo usuario",
                                              font=FUENTES["subtitulo"], text_color=COLORES["texto"])
        self.lbl_titulo_form.pack(anchor="w", padx=20, pady=(15, 15))

        ctk.CTkLabel(contenedor, text="Nombre completo *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.e_nombre = ctk.CTkEntry(contenedor, height=38, font=FUENTES["texto"],
                                       corner_radius=8, placeholder_text="Ej: Juan Pérez García")
        self.e_nombre.pack(fill="x", padx=20, pady=(3, 10))

        ctk.CTkLabel(contenedor, text="Usuario *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.e_usuario = ctk.CTkEntry(contenedor, height=38, font=FUENTES["texto"],
                                        corner_radius=8, placeholder_text="Ej: jperez")
        self.e_usuario.pack(fill="x", padx=20, pady=(3, 10))

        ctk.CTkLabel(contenedor, text="Contraseña", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.e_password = ctk.CTkEntry(contenedor, height=38, font=FUENTES["texto"],
                                         corner_radius=8, show="●",
                                         placeholder_text="Dejar vacío para no cambiar")
        self.e_password.pack(fill="x", padx=20, pady=(3, 10))

        ctk.CTkLabel(contenedor, text="Rol *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.combo_rol_form = ctk.CTkComboBox(contenedor, values=self.ROLES, height=38,
                                                font=FUENTES["texto"], corner_radius=8,
                                                state="readonly")
        self.combo_rol_form.pack(fill="x", padx=20, pady=(3, 10))
        self.combo_rol_form.set(self.ROLES[1])

        ctk.CTkLabel(contenedor, text="Estado *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.combo_estado_form = ctk.CTkComboBox(contenedor, values=self.ESTADOS, height=38,
                                                   font=FUENTES["texto"], corner_radius=8,
                                                   state="readonly")
        self.combo_estado_form.pack(fill="x", padx=20, pady=(3, 15))
        self.combo_estado_form.set("Activo")

        self.btn_guardar = ctk.CTkButton(contenedor, text="💾  Guardar usuario", height=42,
                                           font=FUENTES["boton"], corner_radius=8,
                                           fg_color=COLORES["azul_boton"],
                                           hover_color=COLORES["azul_boton_hover"],
                                           command=self._guardar)
        self.btn_guardar.pack(fill="x", padx=20, pady=(0, 8))

        self.btn_cancelar = ctk.CTkButton(contenedor, text="✖  Cancelar edición", height=38,
                                            font=FUENTES["texto"], corner_radius=8,
                                            fg_color=COLORES["blanco"], hover_color=COLORES["fondo"],
                                            text_color=COLORES["texto"], border_width=1,
                                            border_color=COLORES["borde"],
                                            command=self._limpiar_formulario)
        self.btn_cancelar.pack(fill="x", padx=20, pady=(0, 20))
        self.btn_cancelar.pack_forget()

    # ------------------------------------------------------------------
    def _buscar(self):
        sql = """
            SELECT id_usuario, usuario, rol, estado
            FROM usuarios
            WHERE 1=1
        """
        parametros = []

        texto = self.entry_busqueda.get().strip()
        if texto:
            sql += " AND usuario ILIKE %s"
            parametros.append(f"%{texto}%")

        if self.combo_rol.get() != "Todos":
            sql += " AND rol = %s"
            parametros.append(self.combo_rol.get())

        if self.combo_estado.get() != "Todos":
            sql += " AND estado = %s"
            parametros.append(self.combo_estado.get())

        sql += " ORDER BY id_usuario"

        resp = json.loads(self.cnn.ejecutar_consulta(sql, tuple(parametros) if parametros else None))
        if not resp.get("estado"):
            messagebox.showerror("Error", resp.get("error", "No se pudo consultar."))
            return
        self.usuarios_actuales = resp["registros"]
        self._renderizar()
        self._actualizar_tarjetas()

    def _actualizar_tarjetas(self):
        resp = json.loads(self.cnn.ejecutar_consulta(
            "SELECT COUNT(*) AS total, "
            "COUNT(*) FILTER (WHERE estado='Activo') AS activos, "
            "COUNT(*) FILTER (WHERE estado='Inactivo') AS inactivos "
            "FROM usuarios"
        ))
        if resp.get("estado") and resp["registros"]:
            r = resp["registros"][0]
            self.tarjetas["total"].valor_widget.configure(text=str(r["total"]))
            self.tarjetas["activos"].valor_widget.configure(text=str(r["activos"]))
            self.tarjetas["inactivos"].valor_widget.configure(text=str(r["inactivos"]))

    def _renderizar(self):
        for w in self.contenedor_tabla.winfo_children():
            w.destroy()

        self.lbl_contador.configure(
            text=f"Mostrando {len(self.usuarios_actuales)} usuario{'s' if len(self.usuarios_actuales) != 1 else ''}"
        )

        if not self.usuarios_actuales:
            ctk.CTkLabel(self.contenedor_tabla, text="No se encontraron usuarios",
                         font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
                expand=True, pady=60)
            return

        tabla = Tabla(
            self.contenedor_tabla,
            columnas=["Usuario", "Rol", "Estado", "Acciones"],
            anchos=[3, 2, 2, 2]
        )
        tabla.pack(fill="both", expand=True)

        for u in self.usuarios_actuales:
            self._fila_usuario(tabla, u)

    def _fila_usuario(self, tabla, u):
        fila = ctk.CTkFrame(tabla.cuerpo, fg_color=COLORES["blanco"], corner_radius=0)
        fila.pack(fill="x")
        for i, w in enumerate([3, 2, 2, 2]):
            fila.grid_columnconfigure(i, weight=w)

        ctk.CTkLabel(fila, text=u["usuario"], font=FUENTES["texto_peq"],
                     text_color=COLORES["texto"], anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=8)

        bg_rol, fg_rol = self.COLORES_ROL.get(u["rol"], (COLORES["borde"], COLORES["texto_claro"]))
        ctk.CTkLabel(fila, text=u["rol"], font=("Segoe UI", 10, "bold"),
                     text_color=fg_rol, fg_color=bg_rol, corner_radius=10,
                     padx=10, pady=3).grid(row=0, column=1, sticky="w", padx=12)

        color_estado = (COLORES["verde_claro"], COLORES["verde"]) if u["estado"] == "Activo" \
            else (COLORES["rojo_claro"], COLORES["rojo"])
        ctk.CTkLabel(fila, text=u["estado"], font=("Segoe UI", 10, "bold"),
                     text_color=color_estado[1], fg_color=color_estado[0],
                     corner_radius=10, padx=10, pady=3).grid(row=0, column=2, sticky="w", padx=12)

        acciones = ctk.CTkFrame(fila, fg_color="transparent")
        acciones.grid(row=0, column=3, sticky="w", padx=12)

        ctk.CTkButton(acciones, text="✏", width=32, height=28, font=("Segoe UI", 14),
                       fg_color="transparent", hover_color=COLORES["amarillo_claro"],
                       text_color=COLORES["amarillo"],
                       command=lambda x=u: self._editar(x)).pack(side="left", padx=2)
        ctk.CTkButton(acciones, text="🗑", width=32, height=28, font=("Segoe UI", 14),
                       fg_color="transparent", hover_color=COLORES["rojo_claro"],
                       text_color=COLORES["rojo"],
                       command=lambda x=u: self._eliminar(x)).pack(side="left", padx=2)

    def _limpiar(self):
        self.entry_busqueda.delete(0, "end")
        self.combo_rol.set("Todos")
        self.combo_estado.set("Todos")
        self._buscar()

    # ------------------------------------------------------------------
    def _editar(self, u):
        self.usuario_editando = u
        self.lbl_titulo_form.configure(text=f"✏  Editando: {u['usuario']}")
        self.e_usuario.delete(0, "end")
        self.e_usuario.insert(0, u["usuario"])
        self.e_usuario.configure(state="disabled")
        self.e_password.delete(0, "end")
        self.e_password.configure(placeholder_text="Dejar vacío para conservar la actual")
        self.combo_rol_form.set(u["rol"])
        self.combo_estado_form.set(u["estado"])
        self.btn_guardar.configure(text="💾  Actualizar usuario")
        self.btn_cancelar.pack(fill="x", padx=20, pady=(0, 20))

    def _limpiar_formulario(self):
        self.usuario_editando = None
        self.lbl_titulo_form.configure(text="➕  Nuevo usuario")
        self.e_nombre.delete(0, "end")
        self.e_usuario.configure(state="normal")
        self.e_usuario.delete(0, "end")
        self.e_password.delete(0, "end")
        self.e_password.configure(placeholder_text="Contraseña")
        self.combo_rol_form.set(self.ROLES[1])
        self.combo_estado_form.set("Activo")
        self.btn_guardar.configure(text="💾  Guardar usuario")
        self.btn_cancelar.pack_forget()

    def _guardar(self):
        usuario = self.e_usuario.get().strip()
        password = self.e_password.get().strip()
        rol = self.combo_rol_form.get()
        estado = self.combo_estado_form.get()

        if not usuario:
            messagebox.showwarning("Faltan datos", "El nombre de usuario es obligatorio.")
            return

        if self.usuario_editando:
            if password:
                import hashlib
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                resp = json.loads(self.cnn.ejecutar_consulta(
                    "UPDATE usuarios SET password = %s, rol = %s, estado = %s WHERE id_usuario = %s",
                    (pwd_hash, rol, estado, self.usuario_editando["id_usuario"])
                ))
            else:
                resp = json.loads(self.cnn.ejecutar_consulta(
                    "UPDATE usuarios SET rol = %s, estado = %s WHERE id_usuario = %s",
                    (rol, estado, self.usuario_editando["id_usuario"])
                ))
            if resp.get("estado"):
                messagebox.showinfo("Actualizado", "Usuario actualizado correctamente.")
                self._limpiar_formulario()
                self._buscar()
            else:
                messagebox.showerror("Error", resp.get("error", "No se pudo actualizar."))
        else:
            if not password:
                messagebox.showwarning("Faltan datos", "La contraseña es obligatoria para un usuario nuevo.")
                return
            import hashlib
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            resp = json.loads(self.cnn.ejecutar_consulta(
                "INSERT INTO usuarios (usuario, password, rol, estado) VALUES (%s, %s, %s, %s)",
                (usuario, pwd_hash, rol, estado)
            ))
            if resp.get("estado"):
                messagebox.showinfo("Guardado", f"Usuario '{usuario}' creado correctamente.")
                self._limpiar_formulario()
                self._buscar()
            else:
                if resp.get("codigo") == "23505":
                    messagebox.showerror("Duplicado", "Ya existe un usuario con ese nombre.")
                else:
                    messagebox.showerror("Error", resp.get("error", "No se pudo crear."))

    def _eliminar(self, u):
        if u["usuario"] == "admin.tesoreria":
            messagebox.showwarning("No permitido", "No se puede eliminar al administrador principal.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{u['usuario']}'?"):
            return
        resp = json.loads(self.cnn.ejecutar_consulta(
            "DELETE FROM usuarios WHERE id_usuario = %s", (u["id_usuario"],)
        ))
        if resp.get("estado"):
            messagebox.showinfo("Eliminado", "Usuario eliminado.")
            self._buscar()
        else:
            messagebox.showerror("Error",
                "No se pudo eliminar. Verifique que el usuario no sea responsable de algún bien.")