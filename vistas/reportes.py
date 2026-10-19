import json
import os
import platform
import subprocess
from datetime import date, datetime
from tkinter import messagebox
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES
from reportes.generador import GeneradorReportes


class VistaReportes(ctk.CTkFrame):

    TIPOS_REPORTE = [
        "Inventario general de bienes",
        "Bienes por área",
        "Bienes por estado",
        "Movimientos de bienes",
        "Conciliación físico-contable",
    ]

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self.catalogos = {}
        self.ultimo_reporte = None

        self._cargar_catalogos()
        self._construir()
        self._cargar_recientes()

    def _cargar_catalogos(self):
        resp = json.loads(self.cnn.ejecutar_consulta(
            "SELECT id_area AS id, nombre FROM areas WHERE estado = 'Activo' ORDER BY nombre"
        ))
        self.catalogos["areas"] = resp.get("registros", []) if resp.get("estado") else []

        resp = json.loads(self.cnn.ejecutar_consulta(
            "SELECT id_responsable AS id, nombre FROM responsables WHERE estado = 'Activo' ORDER BY nombre"
        ))
        self.catalogos["responsables"] = resp.get("registros", []) if resp.get("estado") else []

    def _construir(self):
        ctk.CTkLabel(self, text="📊  Reportes", font=FUENTES["titulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Genere y consulte reportes del inventario de bienes.",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 15))

        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        izquierda = ctk.CTkFrame(contenedor, fg_color=COLORES["blanco"], corner_radius=12,
                                  border_width=1, border_color=COLORES["borde"])
        izquierda.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(izquierda, text="📄  Generar reporte", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(izquierda, text="Seleccione los filtros para obtener la información que necesita.",
                     font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=20, pady=(0, 15))

        form = ctk.CTkFrame(izquierda, fg_color="transparent")
        form.pack(fill="x", padx=20)
        for i in range(2):
            form.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(form, text="Tipo de reporte *", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.combo_tipo = ctk.CTkComboBox(form, values=self.TIPOS_REPORTE,
                                            height=38, font=FUENTES["texto"],
                                            corner_radius=8, state="readonly")
        self.combo_tipo.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(3, 12))
        self.combo_tipo.set(self.TIPOS_REPORTE[0])

        ctk.CTkLabel(form, text="Rango de fechas", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).grid(row=0, column=1, sticky="w", padx=(10, 0))
        rango = ctk.CTkFrame(form, fg_color="transparent")
        rango.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(3, 12))
        rango.grid_columnconfigure(0, weight=1)
        rango.grid_columnconfigure(2, weight=1)

        self.e_fecha_ini = ctk.CTkEntry(rango, height=38, font=FUENTES["texto"], corner_radius=8)
        self.e_fecha_ini.grid(row=0, column=0, sticky="ew")
        self.e_fecha_ini.insert(0, date(date.today().year, 1, 1).isoformat())

        ctk.CTkLabel(rango, text="—", font=FUENTES["texto"]).grid(row=0, column=1, padx=8)

        self.e_fecha_fin = ctk.CTkEntry(rango, height=38, font=FUENTES["texto"], corner_radius=8)
        self.e_fecha_fin.grid(row=0, column=2, sticky="ew")
        self.e_fecha_fin.insert(0, date.today().isoformat())

        ctk.CTkLabel(form, text="Área", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).grid(row=2, column=0, sticky="w", padx=(0, 10))
        self.combo_area = ctk.CTkComboBox(
            form, values=["Todas las áreas"] + [a["nombre"] for a in self.catalogos["areas"]],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_area.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(3, 12))
        self.combo_area.set("Todas las áreas")

        ctk.CTkLabel(form, text="Responsable", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).grid(row=2, column=1, sticky="w", padx=(10, 0))
        self.combo_resp = ctk.CTkComboBox(
            form, values=["Todos los responsables"] + [r["nombre"] for r in self.catalogos["responsables"]],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_resp.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(3, 12))
        self.combo_resp.set("Todos los responsables")

        ctk.CTkLabel(form, text="Estado del bien", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).grid(row=4, column=0, sticky="w", padx=(0, 10))
        self.combo_estado = ctk.CTkComboBox(
            form, values=["Todos los estados", "Activo", "Inactivo", "Baja"],
            height=38, font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        self.combo_estado.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(3, 12))
        self.combo_estado.set("Todos los estados")

        ctk.CTkLabel(form, text="Formato de salida", font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).grid(row=4, column=1, sticky="w", padx=(10, 0))
        formatos = ctk.CTkFrame(form, fg_color="transparent")
        formatos.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(3, 12))

        self.var_formato = ctk.StringVar(value="PDF")
        ctk.CTkRadioButton(formatos, text="PDF", variable=self.var_formato, value="PDF",
                            font=FUENTES["texto"]).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(formatos, text="Excel", variable=self.var_formato, value="Excel",
                            font=FUENTES["texto"]).pack(side="left")

        botones = ctk.CTkFrame(izquierda, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=(15, 20))

        ctk.CTkButton(botones, text="👁  Vista previa", height=40, width=160,
                       font=FUENTES["texto"], corner_radius=8,
                       fg_color=COLORES["blanco"], hover_color=COLORES["fondo"],
                       text_color=COLORES["texto"], border_width=1, border_color=COLORES["borde"],
                       command=self._vista_previa).pack(side="left")

        ctk.CTkButton(botones, text="📄  Generar reporte", height=40, width=220,
                       font=FUENTES["boton"], corner_radius=8,
                       fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
                       command=self._generar).pack(side="right")

        # Panel derecho — Reportes recientes
        derecha = ctk.CTkFrame(contenedor, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"], width=340)
        derecha.pack(side="right", fill="y", padx=(20, 0))
        derecha.pack_propagate(False)

        ctk.CTkLabel(derecha, text="🕐  Reportes recientes", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(derecha, text="Consulte los reportes generados recientemente.",
                     font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"],
                     wraplength=280, justify="left").pack(anchor="w", padx=20, pady=(0, 15))

        self.lista_recientes = ctk.CTkScrollableFrame(derecha, fg_color="transparent", height=400)
        self.lista_recientes.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _filtros(self):
        return {
            "area": self.combo_area.get() if self.combo_area.get() != "Todas las áreas" else None,
            "responsable": self.combo_resp.get() if self.combo_resp.get() != "Todos los responsables" else None,
            "estado": self.combo_estado.get() if self.combo_estado.get() != "Todos los estados" else None,
            "fecha_ini": self.e_fecha_ini.get().strip(),
            "fecha_fin": self.e_fecha_fin.get().strip(),
        }

    def _obtener_datos(self):
        f = self._filtros()
        sql = """
            SELECT b.codigo_inventario, b.nombre, b.fecha_adquisicion, b.valor_adquisicion,
                   b.estado, t.nombre AS tipo, a.nombre AS area, r.nombre AS responsable
            FROM bienes b
            JOIN tipos_bien t ON t.id_tipo = b.id_tipo
            JOIN ubicaciones u ON u.id_ubicacion = b.id_ubicacion
            JOIN areas a ON a.id_area = u.id_area
            JOIN responsables r ON r.id_responsable = b.id_responsable
            WHERE b.fecha_adquisicion BETWEEN %s AND %s
        """
        parametros = [f["fecha_ini"], f["fecha_fin"]]

        if f["area"]:
            sql += " AND a.nombre = %s"
            parametros.append(f["area"])
        if f["responsable"]:
            sql += " AND r.nombre = %s"
            parametros.append(f["responsable"])
        if f["estado"]:
            sql += " AND b.estado = %s"
            parametros.append(f["estado"])

        sql += " ORDER BY b.codigo_inventario"
        resp = json.loads(self.cnn.ejecutar_consulta(sql, tuple(parametros)))
        if not resp.get("estado"):
            messagebox.showerror("Error", resp.get("error", "No se pudo consultar."))
            return None
        return resp["registros"]

    def _vista_previa(self):
        datos = self._obtener_datos()
        if datos is None:
            return
        if not datos:
            messagebox.showinfo("Sin datos", "No hay bienes que coincidan con los filtros.")
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Vista previa del reporte")
        ventana.geometry("900x600")
        ventana.configure(fg_color=COLORES["fondo"])

        ctk.CTkLabel(ventana, text="Vista previa del reporte",
                     font=FUENTES["subtitulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(ventana,
                     text=f"Tipo: {self.combo_tipo.get()}   |   Registros: {len(datos)}",
                     font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=20, pady=(0, 10))

        contenedor = ctk.CTkScrollableFrame(ventana, fg_color=COLORES["blanco"], corner_radius=8)
        contenedor.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cabecera = ctk.CTkFrame(contenedor, fg_color=COLORES["azul_claro"], corner_radius=0)
        cabecera.pack(fill="x")
        for i, txt in enumerate(["No. Inventario", "Descripción", "Tipo", "Área", "Responsable", "Estado"]):
            cabecera.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(cabecera, text=txt, font=("Segoe UI", 10, "bold"),
                         text_color=COLORES["azul_oscuro"]).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        for idx, b in enumerate(datos):
            color = COLORES["blanco"] if idx % 2 == 0 else "#fafbfc"
            fila = ctk.CTkFrame(contenedor, fg_color=color, corner_radius=0)
            fila.pack(fill="x")
            valores = [b["codigo_inventario"], b["nombre"], b["tipo"], b["area"],
                       b["responsable"], b["estado"]]
            for i, v in enumerate(valores):
                fila.grid_columnconfigure(i, weight=1)
                ctk.CTkLabel(fila, text=str(v), font=FUENTES["texto_peq"],
                             text_color=COLORES["texto"], anchor="w").grid(
                    row=0, column=i, padx=10, pady=6, sticky="w")

    def _generar(self):
        datos = self._obtener_datos()
        if datos is None:
            return
        if not datos:
            messagebox.showinfo("Sin datos", "No hay bienes que coincidan con los filtros.")
            return

        formato = self.var_formato.get()
        titulo = self.combo_tipo.get()

        try:
            if formato == "PDF":
                ruta = GeneradorReportes.pdf_inventario(
                    datos, titulo=titulo,
                    rango_fechas=f"{self.e_fecha_ini.get()} - {self.e_fecha_fin.get()}"
                )
            else:
                ruta = GeneradorReportes.excel_inventario(datos, titulo=titulo)
        except Exception as e:
            messagebox.showerror("Error al generar", str(e))
            return

        self.ultimo_reporte = {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "tipo": titulo,
            "usuario": "admin.tesoreria",
            "formato": formato,
            "ruta": ruta,
            "registros": len(datos),
        }
        self._agregar_reciente(self.ultimo_reporte)

        if messagebox.askyesno("Reporte generado",
                                f"Reporte generado correctamente.\n\n"
                                f"Archivo: {os.path.basename(ruta)}\n"
                                f"Registros: {len(datos)}\n\n"
                                f"¿Desea abrirlo ahora?"):
            self._abrir_archivo(ruta)

    def _abrir_archivo(self, ruta):
        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(ruta)
            elif sistema == "Darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

    def _cargar_recientes(self):
        for w in self.lista_recientes.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.lista_recientes, text="Aún no hay reportes generados en esta sesión.",
                     font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"],
                     wraplength=280, justify="left").pack(anchor="w", pady=10)

    def _agregar_reciente(self, rep):
        for w in self.lista_recientes.winfo_children():
            w.destroy()

        tarjeta = ctk.CTkFrame(self.lista_recientes, fg_color="#fafbfc", corner_radius=8,
                                border_width=1, border_color=COLORES["borde"])
        tarjeta.pack(fill="x", pady=4)

        icono = "📄" if rep["formato"] == "PDF" else "📊"
        ctk.CTkLabel(tarjeta, text=icono, font=("Segoe UI", 20)).pack(side="left", padx=10, pady=10)

        info = ctk.CTkFrame(tarjeta, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=8)
        ctk.CTkLabel(info, text=rep["tipo"], font=("Segoe UI", 10, "bold"),
                     text_color=COLORES["texto"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"{rep['fecha']} · {rep['registros']} registros",
                     font=("Segoe UI", 9), text_color=COLORES["texto_claro"],
                     anchor="w").pack(anchor="w")

        ctk.CTkButton(tarjeta, text="⬇", width=32, height=32, font=("Segoe UI", 14),
                       fg_color="transparent", hover_color=COLORES["azul_claro"],
                       text_color=COLORES["azul_activo"],
                       command=lambda r=rep["ruta"]: self._abrir_archivo(r)).pack(side="right", padx=8)