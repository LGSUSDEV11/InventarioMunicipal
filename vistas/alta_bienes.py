import json
from datetime import date
from tkinter import messagebox
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES


class VistaAltaBienes(ctk.CTkFrame):

    def __init__(self, master, cnn, bien_editar=None):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self.bien_editar = bien_editar
        self.catalogos = {}
        self.widgets_resumen = {}

        self._cargar_catalogos()
        self._construir()
        if bien_editar:
            self._precargar(bien_editar)

    # ------------------------------------------------------------------
    # Carga de catálogos
    # ------------------------------------------------------------------
    def _cargar_catalogos(self):
        self.catalogos["tipos"] = self._traer(
            "SELECT id_tipo AS id, nombre FROM tipos_bien ORDER BY nombre"
        )
        self.catalogos["responsables"] = self._traer(
            "SELECT id_responsable AS id, nombre FROM responsables WHERE estado = 'Activo' ORDER BY nombre"
        )
        self.catalogos["areas"] = self._traer(
            "SELECT id_area AS id, nombre FROM areas WHERE estado = 'Activo' ORDER BY nombre"
        )
        self.catalogos["ubicaciones"] = self._traer(
            "SELECT u.id_ubicacion AS id, "
            "       e.nombre || ' - ' || a.nombre || COALESCE(' (' || u.descripcion || ')', '') AS nombre "
            "FROM ubicaciones u "
            "JOIN edificios e ON e.id_edificio = u.id_edificio "
            "JOIN areas a ON a.id_area = u.id_area "
            "ORDER BY e.nombre"
        )

    def _traer(self, sql):
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado"):
            return []
        return resp["registros"]

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _construir(self):
        ctk.CTkLabel(self, text="➕  Alta de bienes",
                     font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Registre un nuevo bien en el sistema. Complete la información requerida.",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 15))

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        izquierda = ctk.CTkScrollableFrame(cuerpo, fg_color="transparent", corner_radius=0)
        izquierda.pack(side="left", fill="both", expand=True)

        derecha = ctk.CTkFrame(cuerpo, fg_color="transparent", width=340)
        derecha.pack(side="right", fill="y", padx=(20, 0))
        derecha.pack_propagate(False)

        self._seccion_informacion(izquierda)
        self._seccion_caracteristicas(izquierda)
        self._seccion_asignacion(izquierda)

        self._panel_resumen(derecha)

    def _seccion(self, master, titulo):
        marco = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                              border_width=1, border_color=COLORES["borde"])
        marco.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(marco, text=titulo, font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 10))

        cont = ctk.CTkFrame(marco, fg_color="transparent")
        cont.pack(fill="x", padx=20, pady=(0, 20))
        return cont

    def _campo(self, master, etiqueta, tipo="entry", obligatorio=False, opciones=None,
               columna=0, fila=0, ancho_rel=1, placeholder=""):
        contenedor = ctk.CTkFrame(master, fg_color="transparent")
        contenedor.grid(row=fila, column=columna, sticky="ew", padx=(0, 10), pady=(0, 12))

        texto = etiqueta + (" *" if obligatorio else "")
        ctk.CTkLabel(contenedor, text=texto, font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w")

        if tipo == "entry":
            w = ctk.CTkEntry(contenedor, height=38, font=FUENTES["texto"],
                             corner_radius=8, placeholder_text=placeholder)
        elif tipo == "combo":
            w = ctk.CTkComboBox(contenedor, values=opciones or ["— Seleccione —"],
                                height=38, font=FUENTES["texto"], corner_radius=8,
                                state="readonly")
            w.set(opciones[0] if opciones else "— Seleccione —")
        else:
            w = ctk.CTkEntry(contenedor, height=38, font=FUENTES["texto"], corner_radius=8)

        w.pack(fill="x", pady=(3, 0))
        return w

    def _seccion_informacion(self, master):
        c = self._seccion(master, "📋  Información general")
        for i in range(2):
            c.grid_columnconfigure(i, weight=1)

        self.e_codigo = self._campo(c, "Número de inventario", obligatorio=True,
                                     columna=0, fila=0, placeholder="Ej: BIEN-0011")
        self.e_serie = self._campo(c, "Número de serie", columna=1, fila=0,
                                    placeholder="Ej: SN123456789")

        self.e_nombre = self._campo(c, "Descripción corta", obligatorio=True,
                                     columna=0, fila=1, placeholder="Ej: Computadora Dell OptiPlex")
        self.e_marca = self._campo(c, "Marca", columna=1, fila=1, placeholder="Ej: Dell")
        self.e_modelo = self._campo(c, "Modelo", columna=0, fila=2, placeholder="Ej: OptiPlex 7050")

    def _seccion_caracteristicas(self, master):
        c = self._seccion(master, "📦  Características del bien")
        for i in range(3):
            c.grid_columnconfigure(i, weight=1)

        self.c_tipo = self._campo(c, "Tipo de bien", tipo="combo", obligatorio=True,
                                   opciones=[t["nombre"] for t in self.catalogos["tipos"]],
                                   columna=0, fila=0)
        self.e_fecha = self._campo(c, "Fecha de adquisición", obligatorio=True,
                                    columna=1, fila=0, placeholder="AAAA-MM-DD")
        self.e_fecha.insert(0, date.today().isoformat())
        self.e_valor = self._campo(c, "Valor de adquisición", obligatorio=True,
                                    columna=2, fila=0, placeholder="0.00")

        self.c_estado = self._campo(c, "Estado físico", tipo="combo", obligatorio=True,
                                     opciones=["Activo", "Inactivo", "Baja"],
                                     columna=0, fila=1)
        self.e_descripcion = self._campo(c, "Descripción larga", columna=1, fila=1,
                                          placeholder="Detalles adicionales")

    def _seccion_asignacion(self, master):
        c = self._seccion(master, "👤  Asignación y ubicación")
        for i in range(3):
            c.grid_columnconfigure(i, weight=1)

        self.c_responsable = self._campo(
            c, "Responsable", tipo="combo", obligatorio=True,
            opciones=[r["nombre"] for r in self.catalogos["responsables"]],
            columna=0, fila=0
        )
        self.c_area = self._campo(
            c, "Área", tipo="combo", obligatorio=True,
            opciones=[a["nombre"] for a in self.catalogos["areas"]],
            columna=1, fila=0
        )
        self.c_ubicacion = self._campo(
            c, "Ubicación", tipo="combo", obligatorio=True,
            opciones=[u["nombre"] for u in self.catalogos["ubicaciones"]],
            columna=2, fila=0
        )

    def _panel_resumen(self, master):
        marco = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                              border_width=1, border_color=COLORES["borde"])
        marco.pack(fill="both", expand=True)

        ctk.CTkLabel(marco, text="📄  Resumen del registro", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 10))

        campos = ["Número de inventario", "Descripción", "Tipo de bien", "Marca / Modelo",
                  "Fecha de adquisición", "Valor de adquisición", "Estado físico",
                  "Responsable", "Área", "Ubicación"]

        for campo in campos:
            fila = ctk.CTkFrame(marco, fg_color="transparent")
            fila.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(fila, text=campo, font=FUENTES["texto_peq"],
                         text_color=COLORES["texto_claro"]).pack(side="left")
            valor = ctk.CTkLabel(fila, text="—", font=FUENTES["texto_peq"],
                                  text_color=COLORES["texto"])
            valor.pack(side="right")
            self.widgets_resumen[campo] = valor

        ctk.CTkLabel(
            marco,
            text="ℹ️  Una vez guardado, el bien estará disponible en el sistema.",
            font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"],
            wraplength=280, justify="left"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        botones = ctk.CTkFrame(marco, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkButton(
            botones, text="💾  Guardar bien", height=42,
            font=FUENTES["boton"], corner_radius=8,
            fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
            command=self._guardar
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            botones, text="✖  Cancelar", height=38,
            font=FUENTES["texto"], corner_radius=8,
            fg_color=COLORES["blanco"], hover_color=COLORES["fondo"],
            text_color=COLORES["texto"], border_width=1, border_color=COLORES["borde"],
            command=self._limpiar
        ).pack(fill="x")

    # ------------------------------------------------------------------
    # Lógica de guardado
    # ------------------------------------------------------------------
    def _id_por_nombre(self, lista, nombre):
        return next((x["id"] for x in lista if x["nombre"] == nombre), None)

    def _validar(self):
        if not self.e_codigo.get().strip():
            messagebox.showwarning("Faltan datos", "El número de inventario es obligatorio.")
            return False
        if not self.e_nombre.get().strip():
            messagebox.showwarning("Faltan datos", "La descripción corta es obligatoria.")
            return False
        if self.c_tipo.get() in ("", "— Seleccione —"):
            messagebox.showwarning("Faltan datos", "Seleccione el tipo de bien.")
            return False
        try:
            valor = float(self.e_valor.get().strip())
            if valor < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "El valor de adquisición debe ser un número positivo.")
            return False
        if self.c_responsable.get() in ("", "— Seleccione —"):
            messagebox.showwarning("Faltan datos", "Seleccione un responsable.")
            return False
        if self.c_ubicacion.get() in ("", "— Seleccione —"):
            messagebox.showwarning("Faltan datos", "Seleccione una ubicación.")
            return False
        return True

    def _guardar(self):
        if not self._validar():
            return

        codigo = self.e_codigo.get().strip()
        nombre = self.e_nombre.get().strip()
        descripcion = self.e_descripcion.get().strip()
        fecha = self.e_fecha.get().strip()
        valor = float(self.e_valor.get().strip())
        estado = self.c_estado.get()
        id_tipo = self._id_por_nombre(self.catalogos["tipos"], self.c_tipo.get())
        id_resp = self._id_por_nombre(self.catalogos["responsables"], self.c_responsable.get())
        id_ubic = self._id_por_nombre(self.catalogos["ubicaciones"], self.c_ubicacion.get())

        if self.bien_editar:
            sql = """
                UPDATE bienes
                SET codigo_inventario = %s, nombre = %s, descripcion = %s,
                    fecha_adquisicion = %s, valor_adquisicion = %s, estado = %s,
                    id_tipo = %s, id_ubicacion = %s, id_responsable = %s
                WHERE id_bien = %s
            """
            parametros = (codigo, nombre, descripcion or None, fecha, valor, estado,
                          id_tipo, id_ubic, id_resp, self.bien_editar["id_bien"])
            resp = json.loads(self.cnn.ejecutar_consulta(sql, parametros))
            if resp.get("estado"):
                messagebox.showinfo("Actualizado", "Bien actualizado correctamente.")
                self._limpiar()
            else:
                messagebox.showerror("Error", resp.get("error", "No se pudo actualizar."))
            return

        sql = """
            INSERT INTO bienes
                (codigo_inventario, nombre, descripcion, fecha_adquisicion,
                 valor_adquisicion, estado, id_tipo, id_ubicacion, id_responsable)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_bien
        """
        parametros = (codigo, nombre, descripcion or None, fecha, valor, estado,
                      id_tipo, id_ubic, id_resp)
        resp = json.loads(self.cnn.ejecutar_consulta(sql, parametros))

        if not resp.get("estado"):
            error = resp.get("error", "")
            if resp.get("codigo") == "23505":
                messagebox.showerror("Código duplicado", f"Ya existe un bien con el código '{codigo}'.")
            else:
                messagebox.showerror("Error", error or "No se pudo guardar el bien.")
            return

        resp_id = json.loads(self.cnn.ejecutar_consulta(
            "SELECT id_bien FROM bienes WHERE codigo_inventario = %s", (codigo,)
        ))
        id_bien = resp_id["registros"][0]["id_bien"]

        self.cnn.ejecutar_consulta(
            "INSERT INTO movimientos (id_bien, id_usuario, tipo_movimiento, fecha_movimiento, descripcion) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_bien, 1, "Alta", date.today().isoformat(), "Registro inicial del bien")
        )

        messagebox.showinfo("Guardado", f"Bien registrado correctamente con código {codigo}.")
        self._limpiar()

    def _limpiar(self):
        self.e_codigo.delete(0, "end")
        self.e_nombre.delete(0, "end")
        self.e_descripcion.delete(0, "end")
        self.e_marca.delete(0, "end")
        self.e_modelo.delete(0, "end")
        self.e_serie.delete(0, "end")
        self.e_valor.delete(0, "end")
        self.e_fecha.delete(0, "end")
        self.e_fecha.insert(0, date.today().isoformat())
        self.c_tipo.set(self.catalogos["tipos"][0]["nombre"] if self.catalogos["tipos"] else "")
        self.c_estado.set("Activo")
        self.c_responsable.set(self.catalogos["responsables"][0]["nombre"] if self.catalogos["responsables"] else "")
        self.c_area.set(self.catalogos["areas"][0]["nombre"] if self.catalogos["areas"] else "")
        self.c_ubicacion.set(self.catalogos["ubicaciones"][0]["nombre"] if self.catalogos["ubicaciones"] else "")

    def _precargar(self, bien):
        self.e_codigo.insert(0, bien.get("codigo_inventario", ""))
        self.e_nombre.insert(0, bien.get("nombre", ""))
        self.e_descripcion.insert(0, bien.get("descripcion") or "")
        self.e_fecha.delete(0, "end")
        self.e_fecha.insert(0, str(bien.get("fecha_adquisicion", "")))
        self.e_valor.insert(0, str(bien.get("valor_adquisicion", "")))