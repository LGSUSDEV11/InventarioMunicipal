import json
from datetime import date
from tkinter import messagebox
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES
from componentes.tabla import Tabla


class VistaConciliacion(ctk.CTkFrame):

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self.catalogos = {}
        self.resultados = []
        self.resumen = {}

        self._cargar_catalogos()
        self._construir()

    def _cargar_catalogos(self):
        self.catalogos["areas"] = self._traer(
            "SELECT id_area AS id, nombre FROM areas WHERE estado = 'Activo' ORDER BY nombre"
        )

    def _traer(self, sql):
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado"):
            return []
        return resp["registros"]

    # ------------------------------------------------------------------
    def _construir(self):
        ctk.CTkLabel(self, text="⚖️  Conciliación físico-contable",
                    font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self,
                    text="Compare la información de los bienes entre el registro físico y los datos contables.",
                    font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 15))

        filtros = ctk.CTkFrame(self, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"])
        filtros.pack(fill="x", padx=30, pady=(0, 15))

        fila = ctk.CTkFrame(filtros, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=15)
        for i in range(5):
            fila.grid_columnconfigure(i, weight=1)

        self.e_fecha_ini = self._campo(fila, "Fecha inicial", 0)
        self.e_fecha_ini.insert(0, date(date.today().year, 1, 1).isoformat())

        self.e_fecha_fin = self._campo(fila, "Fecha final", 1)
        self.e_fecha_fin.insert(0, date.today().isoformat())

        self.combo_area = self._combo(fila, "Área", 2,
            ["Todas"] + [a["nombre"] for a in self.catalogos["areas"]])

        self.combo_estado = self._combo(fila, "Estado", 3,
            ["Todos", "Activo", "Inactivo", "Baja"])

        boton = ctk.CTkFrame(fila, fg_color="transparent")
        boton.grid(row=0, column=4, padx=(5, 0), sticky="ew")
        ctk.CTkLabel(boton, text=" ", font=FUENTES["texto_peq"]).pack()
        ctk.CTkButton(boton, text="🔍  Realizar conciliación", height=38,
                    font=FUENTES["boton"], corner_radius=8,
                    fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
                    command=self._conciliar).pack(fill="x", pady=(3, 0))

        # Tarjetas de resumen
        fila_stats = ctk.CTkFrame(self, fg_color="transparent")
        fila_stats.pack(fill="x", padx=30, pady=(0, 15))
        for i in range(4):
            fila_stats.grid_columnconfigure(i, weight=1)

        self.tarjetas = {}
        definiciones = [
            ("coincidentes", "Coincidentes", "✅", COLORES["verde"], COLORES["verde_claro"]),
            ("diferencias", "Diferencias de valor", "⚠️", COLORES["amarillo"], COLORES["amarillo_claro"]),
            ("sin_contable", "Sin registro contable", "❌", COLORES["rojo"], COLORES["rojo_claro"]),
            ("sin_fisico", "Registros sin bien físico", "📦", COLORES["azul_activo"], COLORES["azul_claro"]),
        ]
        for i, (clave, titulo, icono, color, color_bg) in enumerate(definiciones):
            tarjeta = self._tarjeta(fila_stats, titulo, icono, color, color_bg)
            tarjeta.grid(row=0, column=i, padx=8, sticky="nsew")
            self.tarjetas[clave] = tarjeta

        ctk.CTkLabel(self, text="Resultado de la conciliación",
                     font=FUENTES["subtitulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(5, 5))

        self.contenedor_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        # Panel derecho
        panel_der = ctk.CTkFrame(self, fg_color=COLORES["blanco"], corner_radius=12,
                                  border_width=1, border_color=COLORES["borde"])
        panel_der.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(panel_der, text="📝  Observaciones", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 5))

        self.txt_observaciones = ctk.CTkTextbox(panel_der, height=70,
                                font=FUENTES["texto"], corner_radius=8)
        self.txt_observaciones.pack(fill="x", padx=20, pady=(0, 10))

        botones = ctk.CTkFrame(panel_der, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(botones, text="💾  Guardar conciliación", height=40,
                       font=FUENTES["boton"], corner_radius=8, width=240,
                       fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
                       command=self._guardar).pack(side="left", padx=(0, 10))
        ctk.CTkButton(botones, text="📄  Generar reporte", height=40,
                       font=FUENTES["texto"], corner_radius=8, width=200,
                       fg_color=COLORES["blanco"], hover_color=COLORES["fondo"],
                       text_color=COLORES["texto"], border_width=1, border_color=COLORES["borde"],
                       command=lambda: messagebox.showinfo("Reporte", "El reporte de conciliación se implementará en el módulo de Reportes.")).pack(side="left")

    def _campo(self, master, etiqueta, columna):
        cont = ctk.CTkFrame(master, fg_color="transparent")
        cont.grid(row=0, column=columna, padx=5, sticky="ew")
        ctk.CTkLabel(cont, text=etiqueta, font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w")
        entry = ctk.CTkEntry(cont, height=38, font=FUENTES["texto"], corner_radius=8)
        entry.pack(fill="x", pady=(3, 0))
        return entry

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

    def _tarjeta(self, master, titulo, icono, color, color_bg):
        marco = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                              border_width=1, border_color=COLORES["borde"])
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=18, pady=(15, 5))

        circulo = ctk.CTkFrame(fila, fg_color=color_bg, width=44, height=44, corner_radius=22)
        circulo.pack(side="left")
        circulo.pack_propagate(False)
        ctk.CTkLabel(circulo, text=icono, font=("Segoe UI", 20), text_color=color).pack(expand=True)

        ctk.CTkLabel(fila, text=titulo, font=FUENTES["texto"],
                     text_color=COLORES["texto_claro"], wraplength=140, justify="left").pack(
            side="left", padx=10)

        valor = ctk.CTkLabel(marco, text="0", font=FUENTES["stat"], text_color=COLORES["texto"])
        valor.pack(anchor="w", padx=18, pady=(0, 15))
        marco.valor_widget = valor
        return marco

    # ------------------------------------------------------------------
    def _conciliar(self):
        area = self.combo_area.get()
        estado = self.combo_estado.get()
        f_ini = self.e_fecha_ini.get().strip()
        f_fin = self.e_fecha_fin.get().strip()

        sql = """
            SELECT b.id_bien, b.codigo_inventario, b.nombre, b.valor_adquisicion,
                   b.estado, rc.valor_contable
            FROM bienes b
            LEFT JOIN registros_contables rc 
                ON rc.id_bien = b.id_bien
               AND rc.fecha_registro BETWEEN %s AND %s
            JOIN ubicaciones u ON u.id_ubicacion = b.id_ubicacion
            JOIN areas a ON a.id_area = u.id_area
            WHERE 1=1
        """
        parametros = [f_ini, f_fin]

        if area != "Todas":
            sql += " AND a.nombre = %s"
            parametros.append(area)
        if estado != "Todos":
            sql += " AND b.estado = %s"
            parametros.append(estado)

        sql += " ORDER BY b.codigo_inventario"

        resp = json.loads(self.cnn.ejecutar_consulta(sql, tuple(parametros)))
        if not resp.get("estado"):
            messagebox.showerror("Error", resp.get("error", "No se pudo conciliar."))
            return

        filas = resp["registros"]
        resultados = []
        coincidentes = diferencias = sin_contable = 0

        for f in filas:
            v_fisico = float(f["valor_adquisicion"] or 0)
            v_contable = float(f["valor_contable"]) if f["valor_contable"] is not None else None

            if v_contable is None:
                resultado = "Sin registro contable"
                color = COLORES["rojo"]
                sin_contable += 1
                diferencia = None
            elif abs(v_fisico - v_contable) < 0.01:
                resultado = "Coincide"
                color = COLORES["verde"]
                coincidentes += 1
                diferencia = 0.0
            else:
                resultado = "Diferencia"
                color = COLORES["amarillo"]
                diferencias += 1
                diferencia = v_fisico - v_contable

            resultados.append({
                "id_bien": f["id_bien"],
                "codigo": f["codigo_inventario"],
                "nombre": f["nombre"],
                "v_fisico": v_fisico,
                "v_contable": v_contable,
                "diferencia": diferencia,
                "resultado": resultado,
                "color": color,
            })

        self.resultados = resultados
        self.resumen = {
            "coincidentes": coincidentes,
            "diferencias": diferencias,
            "sin_contable": sin_contable,
            "sin_fisico": 0,
            "total": len(resultados),
            "f_ini": f_ini,
            "f_fin": f_fin,
            "area": area,
        }

        self._actualizar_tarjetas()
        self._renderizar()

    def _actualizar_tarjetas(self):
        self.tarjetas["coincidentes"].valor_widget.configure(text=str(self.resumen["coincidentes"]))
        self.tarjetas["diferencias"].valor_widget.configure(text=str(self.resumen["diferencias"]))
        self.tarjetas["sin_contable"].valor_widget.configure(text=str(self.resumen["sin_contable"]))
        self.tarjetas["sin_fisico"].valor_widget.configure(text=str(self.resumen["sin_fisico"]))

    def _renderizar(self):
        for w in self.contenedor_tabla.winfo_children():
            w.destroy()

        if not self.resultados:
            ctk.CTkLabel(self.contenedor_tabla, text="No hay resultados. Presione 'Realizar conciliación'.",
                         font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(expand=True, pady=40)
            return

        tabla = Tabla(
            self.contenedor_tabla,
            columnas=["No. Inventario", "Bien", "Valor físico", "Valor contable", "Diferencia", "Resultado"],
            anchos=[2, 4, 2, 2, 2, 2]
        )
        tabla.pack(fill="both", expand=True)

        for r in self.resultados:
            fila = ctk.CTkFrame(tabla.cuerpo, fg_color=COLORES["blanco"], corner_radius=0)
            fila.pack(fill="x")
            for i, w in enumerate([2, 4, 2, 2, 2, 2]):
                fila.grid_columnconfigure(i, weight=w)

            ctk.CTkLabel(fila, text=r["codigo"], font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=8)
            ctk.CTkLabel(fila, text=r["nombre"], font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=1, sticky="w", padx=12)
            ctk.CTkLabel(fila, text=f"${r['v_fisico']:,.2f}", font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=2, sticky="w", padx=12)
            vc = f"${r['v_contable']:,.2f}" if r["v_contable"] is not None else "—"
            ctk.CTkLabel(fila, text=vc, font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=3, sticky="w", padx=12)
            dif = f"${r['diferencia']:,.2f}" if r["diferencia"] is not None else "—"
            ctk.CTkLabel(fila, text=dif, font=FUENTES["texto_peq"],
                         text_color=COLORES["texto"], anchor="w").grid(row=0, column=4, sticky="w", padx=12)
            ctk.CTkLabel(fila, text=r["resultado"], font=("Segoe UI", 10, "bold"),
                         text_color=r["color"], anchor="w").grid(row=0, column=5, sticky="w", padx=12)

    def _guardar(self):
        if not self.resultados:
            messagebox.showwarning("Sin datos", "Primero realice la conciliación.")
            return

        observaciones = self.txt_observaciones.get("1.0", "end").strip()
        guardados = 0

        for r in self.resultados:
            if r["resultado"] == "Coincide":
                tipo_db = "Conciliado"
            elif r["resultado"] == "Diferencia":
                tipo_db = "Diferencia"
            else:
                tipo_db = "Pendiente"

            resp = json.loads(self.cnn.ejecutar_consulta(
                "INSERT INTO conciliaciones (id_bien, id_usuario, fecha_revision, resultado, observaciones) "
                "VALUES (%s, %s, %s, %s, %s)",
                (r["id_bien"], 1, date.today().isoformat(), tipo_db, observaciones or None)
            ))
            if resp.get("estado"):
                guardados += 1

        messagebox.showinfo("Guardado", f"Conciliación registrada para {guardados} bienes.")