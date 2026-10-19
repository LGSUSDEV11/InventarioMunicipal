import json
from datetime import date
from tkinter import messagebox
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES
from componentes.tabla import Tabla


class VistaMovimientos(ctk.CTkFrame):

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self.catalogos = {}
        self.movimientos_actuales = []
        self.bien_seleccionado = None

        self._cargar_catalogos()
        self._construir()
        self._buscar()

    # ------------------------------------------------------------------
    # Catálogos
    # ------------------------------------------------------------------
    def _cargar_catalogos(self):
        self.catalogos["bienes"] = self._traer(
            "SELECT id_bien AS id, codigo_inventario || ' - ' || nombre AS nombre "
            "FROM bienes ORDER BY codigo_inventario"
        )
        self.catalogos["responsables"] = self._traer(
            "SELECT id_responsable AS id, nombre FROM responsables WHERE estado = 'Activo' ORDER BY nombre"
        )
        self.catalogos["ubicaciones"] = self._traer(
            "SELECT u.id_ubicacion AS id, "
            "       e.nombre || ' - ' || a.nombre AS nombre "
            "FROM ubicaciones u "
            "JOIN edificios e ON e.id_edificio = u.id_edificio "
            "JOIN areas a ON a.id_area = u.id_area "
            "ORDER BY e.nombre"
        )
        self.catalogos["usuarios"] = self._traer(
            "SELECT id_usuario AS id, usuario FROM usuarios ORDER BY usuario"
        )

    def _traer(self, sql):
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado"):
            return []
        return resp["registros"]

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------
    def _construir(self):
        ctk.CTkLabel(self, text="🔄  Movimientos", font=FUENTES["titulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Historial y registro de movimientos de bienes",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 15))

        filtros = ctk.CTkFrame(self, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"])
        filtros.pack(fill="x", padx=30, pady=(0, 15))

        fila1 = ctk.CTkFrame(filtros, fg_color="transparent")
        fila1.pack(fill="x", padx=20, pady=(15, 8))

        self.entry_bien = ctk.CTkEntry(fila1, placeholder_text="🔎  No. inventario o bien...",
                                        height=38, font=FUENTES["texto"], corner_radius=8, width=320)
        self.entry_bien.pack(side="left", padx=(0, 10))

        ctk.CTkButton(fila1, text="Buscar", width=110, height=38, font=FUENTES["boton"],
                       corner_radius=8, fg_color=COLORES["azul_boton"],
                       hover_color=COLORES["azul_boton_hover"],
                       command=self._buscar).pack(side="left")

        ctk.CTkButton(fila1, text="Limpiar", width=110, height=38, font=FUENTES["texto"],
                       corner_radius=8, fg_color=COLORES["borde"], hover_color="#d1d5db",
                       text_color=COLORES["texto"],
                       command=self._limpiar).pack(side="left", padx=10)

        fila2 = ctk.CTkFrame(filtros, fg_color="transparent")
        fila2.pack(fill="x", padx=20, pady=(8, 15))
        for i in range(3):
            fila2.grid_columnconfigure(i, weight=1)

        self.combo_tipo = self._combo(fila2, "Tipo de movimiento", 0,
            ["Todos", "Alta", "Baja", "Cambio de responsable",
             "Cambio de ubicación", "Mantenimiento", "Otro"])
        self.combo_usuario = self._combo(fila2, "Usuario", 1,
            ["Todos"] + [u["usuario"] for u in self.catalogos["usuarios"]])
        self.combo_fecha = self._combo(fila2, "Rango de fecha", 2,
            ["Todas", "Hoy", "Última semana", "Último mes", "Último año"])

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        izquierda = ctk.CTkFrame(cuerpo, fg_color="transparent")
        izquierda.pack(side="left", fill="both", expand=True)

        derecha = ctk.CTkFrame(cuerpo, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"], width=340)
        derecha.pack(side="right", fill="y", padx=(20, 0))
        derecha.pack_propagate(False)

        self.lbl_contador = ctk.CTkLabel(izquierda, text="Mostrando 0 movimientos",
                                           font=FUENTES["texto_peq"],
                                           text_color=COLORES["texto_claro"])
        self.lbl_contador.pack(anchor="w", pady=(0, 5))

        self.contenedor_tabla = ctk.CTkFrame(izquierda, fg_color="transparent")
        self.contenedor_tabla.pack(fill="both", expand=True)

        self._panel_registro(derecha)

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

    def _panel_registro(self, master):
        ctk.CTkLabel(master, text="➕  Registrar movimiento", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(master, text="Selecciona el tipo de movimiento y completa la información.",
                     font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"],
                     wraplength=280, justify="left").pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkLabel(master, text="Bien *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.combo_bien = ctk.CTkComboBox(
            master, values=["— Seleccione —"] + [b["nombre"] for b in self.catalogos["bienes"]],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_bien.pack(fill="x", padx=20, pady=(3, 12))
        self.combo_bien.set("— Seleccione —")

        ctk.CTkLabel(master, text="Tipo de movimiento *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.combo_tipo_form = ctk.CTkComboBox(
            master, values=["Alta", "Baja", "Cambio de responsable",
                            "Cambio de ubicación", "Mantenimiento", "Otro"],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_tipo_form.pack(fill="x", padx=20, pady=(3, 12))
        self.combo_tipo_form.set("Cambio de responsable")

        ctk.CTkLabel(master, text="Fecha *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.entry_fecha = ctk.CTkEntry(master, height=38, font=FUENTES["texto"],
                                          corner_radius=8)
        self.entry_fecha.pack(fill="x", padx=20, pady=(3, 12))
        self.entry_fecha.insert(0, date.today().isoformat())

        ctk.CTkLabel(master, text="Responsable nuevo", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.combo_responsable = ctk.CTkComboBox(
            master, values=["— Ninguno —"] + [r["nombre"] for r in self.catalogos["responsables"]],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_responsable.pack(fill="x", padx=20, pady=(3, 12))
        self.combo_responsable.set("— Ninguno —")

        ctk.CTkLabel(master, text="Ubicación nueva", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.combo_ubicacion = ctk.CTkComboBox(
            master, values=["— Ninguna —"] + [u["nombre"] for u in self.catalogos["ubicaciones"]],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_ubicacion.pack(fill="x", padx=20, pady=(3, 12))
        self.combo_ubicacion.set("— Ninguna —")

        ctk.CTkLabel(master, text="Observaciones", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
        self.txt_observaciones = ctk.CTkTextbox(master, height=70, font=FUENTES["texto"],
                                                  corner_radius=8)
        self.txt_observaciones.pack(fill="x", padx=20, pady=(3, 15))

        ctk.CTkButton(master, text="💾  Registrar movimiento", height=42,
                       font=FUENTES["boton"], corner_radius=8,
                       fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
                       command=self._registrar).pack(fill="x", padx=20, pady=(0, 20))

    # ------------------------------------------------------------------
    # Búsqueda y render
    # ------------------------------------------------------------------
    def _buscar(self):
        sql = """
            SELECT m.id_movimiento, m.tipo_movimiento, m.fecha_movimiento, m.descripcion,
                   b.codigo_inventario, b.nombre AS bien, b.id_bien,
                   u.usuario, b.estado
            FROM movimientos m
            JOIN bienes b ON b.id_bien = m.id_bien
            JOIN usuarios u ON u.id_usuario = m.id_usuario
            WHERE 1=1
        """
        parametros = []

        texto = self.entry_bien.get().strip()
        if texto:
            sql += " AND (b.codigo_inventario ILIKE %s OR b.nombre ILIKE %s)"
            parametros.extend([f"%{texto}%", f"%{texto}%"])

        if self.combo_tipo.get() != "Todos":
            sql += " AND m.tipo_movimiento = %s"
            parametros.append(self.combo_tipo.get())

        if self.combo_usuario.get() != "Todos":
            sql += " AND u.usuario = %s"
            parametros.append(self.combo_usuario.get())

        rango = self.combo_fecha.get()
        if rango == "Hoy":
            sql += " AND m.fecha_movimiento = CURRENT_DATE"
        elif rango == "Última semana":
            sql += " AND m.fecha_movimiento >= CURRENT_DATE - INTERVAL '7 days'"
        elif rango == "Último mes":
            sql += " AND m.fecha_movimiento >= CURRENT_DATE - INTERVAL '30 days'"
        elif rango == "Último año":
            sql += " AND m.fecha_movimiento >= CURRENT_DATE - INTERVAL '365 days'"

        sql += " ORDER BY m.fecha_movimiento DESC, m.id_movimiento DESC"

        resp = json.loads(self.cnn.ejecutar_consulta(sql, tuple(parametros) if parametros else None))
        if not resp.get("estado"):
            messagebox.showerror("Error", resp.get("error", "No se pudo consultar."))
            return
        self.movimientos_actuales = resp["registros"]
        self._renderizar()

    def _renderizar(self):
        for w in self.contenedor_tabla.winfo_children():
            w.destroy()

        self.lbl_contador.configure(
            text=f"Mostrando {len(self.movimientos_actuales)} movimiento{'s' if len(self.movimientos_actuales) != 1 else ''}"
        )

        if not self.movimientos_actuales:
            ctk.CTkLabel(self.contenedor_tabla,
                         text="No se encontraron movimientos",
                         font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
                expand=True, pady=60)
            return

        tabla = Tabla(
            self.contenedor_tabla,
            columnas=["No. Inventario", "Bien", "Tipo", "Fecha", "Usuario", "Observaciones"],
            anchos=[2, 3, 2, 2, 2, 4]
        )
        tabla.pack(fill="both", expand=True)

        for m in self.movimientos_actuales:
            fila = ctk.CTkFrame(tabla.cuerpo, fg_color=COLORES["blanco"], corner_radius=0)
            fila.pack(fill="x")
            for i, w in enumerate([2, 3, 2, 2, 2, 4]):
                fila.grid_columnconfigure(i, weight=w)

            ctk.CTkLabel(fila, text=m["codigo_inventario"], font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=8)
            ctk.CTkLabel(fila, text=m["bien"], font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=1, sticky="w", padx=12)
            ctk.CTkLabel(fila, text=m["tipo_movimiento"], font=FUENTES["texto_peq"],
                         text_color=COLORES["azul_activo"], anchor="w").grid(row=0, column=2, sticky="w", padx=12)
            ctk.CTkLabel(fila, text=str(m["fecha_movimiento"]), font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=3, sticky="w", padx=12)
            ctk.CTkLabel(fila, text=m["usuario"], font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=4, sticky="w", padx=12)
            ctk.CTkLabel(fila, text=(m["descripcion"] or "—")[:60], font=FUENTES["texto_peq"],
                         text_color=COLORES["texto_claro"], anchor="w").grid(row=0, column=5, sticky="w", padx=12)

    def _limpiar(self):
        self.entry_bien.delete(0, "end")
        self.combo_tipo.set("Todos")
        self.combo_usuario.set("Todos")
        self.combo_fecha.set("Todas")
        self._buscar()

    # ------------------------------------------------------------------
    # Registro de movimiento
    # ------------------------------------------------------------------
    def _registrar(self):
        if self.combo_bien.get() == "— Seleccione —":
            messagebox.showwarning("Faltan datos", "Seleccione el bien.")
            return
        if not self.entry_fecha.get().strip():
            messagebox.showwarning("Faltan datos", "Ingrese la fecha del movimiento.")
            return

        id_bien = next((b["id"] for b in self.catalogos["bienes"]
                        if b["nombre"] == self.combo_bien.get()), None)
        if id_bien is None:
            messagebox.showerror("Error", "No se pudo identificar el bien.")
            return

        tipo = self.combo_tipo_form.get()
        fecha = self.entry_fecha.get().strip()
        observaciones = self.txt_observaciones.get("1.0", "end").strip()

        resp = json.loads(self.cnn.ejecutar_consulta(
            "INSERT INTO movimientos (id_bien, id_usuario, tipo_movimiento, fecha_movimiento, descripcion) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_bien, 1, tipo, fecha, observaciones or None)
        ))
        if not resp.get("estado"):
            messagebox.showerror("Error", resp.get("error", "No se pudo registrar."))
            return

        if tipo == "Cambio de responsable" and self.combo_responsable.get() != "— Ninguno —":
            id_resp = next((r["id"] for r in self.catalogos["responsables"]
                            if r["nombre"] == self.combo_responsable.get()), None)
            if id_resp:
                self.cnn.ejecutar_consulta(
                    "UPDATE bienes SET id_responsable = %s WHERE id_bien = %s",
                    (id_resp, id_bien)
                )

        if tipo == "Cambio de ubicación" and self.combo_ubicacion.get() != "— Ninguna —":
            id_ubic = next((u["id"] for u in self.catalogos["ubicaciones"]
                            if u["nombre"] == self.combo_ubicacion.get()), None)
            if id_ubic:
                self.cnn.ejecutar_consulta(
                    "UPDATE bienes SET id_ubicacion = %s WHERE id_bien = %s",
                    (id_ubic, id_bien)
                )

        if tipo == "Baja":
            self.cnn.ejecutar_consulta(
                "UPDATE bienes SET estado = 'Baja' WHERE id_bien = %s", (id_bien,)
            )

        if tipo == "Mantenimiento":
            self.cnn.ejecutar_consulta(
                "UPDATE bienes SET estado = 'Inactivo' WHERE id_bien = %s", (id_bien,)
            )

        messagebox.showinfo("Registrado", "Movimiento registrado correctamente.")
        self._limpiar_formulario()
        self._buscar()

    def _limpiar_formulario(self):
        self.combo_bien.set("— Seleccione —")
        self.combo_tipo_form.set("Cambio de responsable")
        self.combo_responsable.set("— Ninguno —")
        self.combo_ubicacion.set("— Ninguna —")
        self.txt_observaciones.delete("1.0", "end")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, date.today().isoformat())
