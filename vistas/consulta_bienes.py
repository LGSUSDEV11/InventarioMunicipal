import json
import customtkinter as ctk
from tkinter import messagebox
from componentes.tema import COLORES, FUENTES
from componentes.tabla import Tabla


class VistaConsultaBienes(ctk.CTkFrame):

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self.catalogos = {}
        self.bienes_actuales = []
        self._construir()
        self._cargar_catalogos()
        self._buscar()

    def _construir(self):
        ctk.CTkLabel(self, text="🔍  Consulta de bienes",
                     font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Busque y filtre los bienes del inventario municipal",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 20))

        filtros = ctk.CTkFrame(self, fg_color=COLORES["blanco"], corner_radius=12,
                                border_width=1, border_color=COLORES["borde"])
        filtros.pack(fill="x", padx=30, pady=(0, 15))

        fila1 = ctk.CTkFrame(filtros, fg_color="transparent")
        fila1.pack(fill="x", padx=20, pady=(15, 8))

        self.entry_busqueda = ctk.CTkEntry(
            fila1, placeholder_text="🔎  Buscar por código, nombre o descripción...",
            height=38, font=FUENTES["texto"], corner_radius=8, width=420
        )
        self.entry_busqueda.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila1, text="Buscar", width=110, height=38,
            font=FUENTES["boton"], corner_radius=8,
            fg_color=COLORES["azul_boton"], hover_color=COLORES["azul_boton_hover"],
            command=self._buscar
        ).pack(side="left")

        ctk.CTkButton(
            fila1, text="Limpiar", width=110, height=38,
            font=FUENTES["texto"], corner_radius=8,
            fg_color=COLORES["borde"], hover_color="#d1d5db",
            text_color=COLORES["texto"],
            command=self._limpiar
        ).pack(side="left", padx=10)

        fila2 = ctk.CTkFrame(filtros, fg_color="transparent")
        fila2.pack(fill="x", padx=20, pady=(8, 15))
        for i in range(4):
            fila2.grid_columnconfigure(i, weight=1)

        self.combo_tipo = self._combo_filtro(fila2, "Tipo de bien", 0)
        self.combo_area = self._combo_filtro(fila2, "Área", 1)
        self.combo_responsable = self._combo_filtro(fila2, "Responsable", 2)
        self.combo_estado = self._combo_filtro(fila2, "Estado", 3)

        self.lbl_contador = ctk.CTkLabel(
            self, text="Mostrando 0 bienes",
            font=FUENTES["texto_peq"], text_color=COLORES["texto_claro"]
        )
        self.lbl_contador.pack(anchor="w", padx=35, pady=(5, 5))

        self.contenedor_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def _combo_filtro(self, master, etiqueta, columna):
        contenedor = ctk.CTkFrame(master, fg_color="transparent")
        contenedor.grid(row=0, column=columna, padx=5, sticky="ew")

        ctk.CTkLabel(contenedor, text=etiqueta, font=FUENTES["texto_peq"],
                     text_color=COLORES["texto_claro"]).pack(anchor="w")

        combo = ctk.CTkComboBox(
            contenedor, values=["Todos"], height=38,
            font=FUENTES["texto"], corner_radius=8, state="readonly"
        )
        combo.pack(fill="x", pady=(3, 0))
        combo.set("Todos")
        return combo

    def _cargar_catalogos(self):
        self.catalogos["tipos"] = self._traer_catalogo(
            "SELECT id_tipo AS id, nombre FROM tipos_bien ORDER BY nombre"
        )
        self.catalogos["areas"] = self._traer_catalogo(
            "SELECT id_area AS id, nombre FROM areas WHERE estado = 'Activo' ORDER BY nombre"
        )
        self.catalogos["responsables"] = self._traer_catalogo(
            "SELECT id_responsable AS id, nombre FROM responsables WHERE estado = 'Activo' ORDER BY nombre"
        )

        self.combo_tipo.configure(values=["Todos"] + [t["nombre"] for t in self.catalogos["tipos"]])
        self.combo_area.configure(values=["Todos"] + [a["nombre"] for a in self.catalogos["areas"]])
        self.combo_responsable.configure(values=["Todos"] + [r["nombre"] for r in self.catalogos["responsables"]])
        self.combo_estado.configure(values=["Todos", "Activo", "Inactivo", "Baja"])

    def _traer_catalogo(self, sql):
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado"):
            return []
        return resp["registros"]

    def _buscar(self):
        sql = """
            SELECT b.id_bien, b.codigo_inventario, b.nombre, b.descripcion,
                   b.fecha_adquisicion, b.valor_adquisicion, b.estado,
                   t.nombre AS tipo, a.nombre AS area, r.nombre AS responsable,
                   u.descripcion AS ubicacion
            FROM bienes b
            JOIN tipos_bien t ON t.id_tipo = b.id_tipo
            JOIN ubicaciones u ON u.id_ubicacion = b.id_ubicacion
            JOIN areas a ON a.id_area = u.id_area
            JOIN responsables r ON r.id_responsable = b.id_responsable
            WHERE 1=1
        """
        parametros = []

        texto = self.entry_busqueda.get().strip()
        if texto:
            sql += " AND (b.codigo_inventario ILIKE %s OR b.nombre ILIKE %s OR b.descripcion ILIKE %s)"
            patron = f"%{texto}%"
            parametros.extend([patron, patron, patron])

        if self.combo_tipo.get() != "Todos":
            id_tipo = next((t["id"] for t in self.catalogos["tipos"] if t["nombre"] == self.combo_tipo.get()), None)
            if id_tipo:
                sql += " AND b.id_tipo = %s"
                parametros.append(id_tipo)

        if self.combo_area.get() != "Todos":
            id_area = next((a["id"] for a in self.catalogos["areas"] if a["nombre"] == self.combo_area.get()), None)
            if id_area:
                sql += " AND a.id_area = %s"
                parametros.append(id_area)

        if self.combo_responsable.get() != "Todos":
            id_resp = next((r["id"] for r in self.catalogos["responsables"] if r["nombre"] == self.combo_responsable.get()), None)
            if id_resp:
                sql += " AND b.id_responsable = %s"
                parametros.append(id_resp)

        if self.combo_estado.get() != "Todos":
            sql += " AND b.estado = %s"
            parametros.append(self.combo_estado.get())

        sql += " ORDER BY b.id_bien"

        resp = json.loads(self.cnn.ejecutar_consulta(sql, tuple(parametros) if parametros else None))
        if not resp.get("estado"):
            messagebox.showerror("Error", f"Error al consultar bienes:\n{resp.get('error', '')}")
            return

        self.bienes_actuales = resp["registros"]
        self._renderizar()

    def _renderizar(self):
        for w in self.contenedor_tabla.winfo_children():
            w.destroy()

        self.lbl_contador.configure(
            text=f"Mostrando {len(self.bienes_actuales)} bien{'es' if len(self.bienes_actuales) != 1 else ''}"
        )

        if not self.bienes_actuales:
            ctk.CTkLabel(
                self.contenedor_tabla,
                text="No se encontraron bienes con los filtros aplicados",
                font=FUENTES["texto"], text_color=COLORES["texto_claro"]
            ).pack(expand=True, pady=60)
            return

        tabla = Tabla(
            self.contenedor_tabla,
            columnas=["No. Inventario", "Descripción", "Tipo", "Área", "Responsable", "Estado", "Acciones"],
            anchos=[2, 4, 2, 2, 2, 1, 2]
        )
        tabla.pack(fill="both", expand=True)

        for bien in self.bienes_actuales:
            self._agregar_fila(tabla, bien)

    def _agregar_fila(self, tabla, bien):
        contenedor = ctk.CTkFrame(tabla.cuerpo, fg_color=COLORES["blanco"], corner_radius=0)
        contenedor.pack(fill="x")
        contenedor.grid_columnconfigure(0, weight=2)
        contenedor.grid_columnconfigure(1, weight=4)
        contenedor.grid_columnconfigure(2, weight=2)
        contenedor.grid_columnconfigure(3, weight=2)
        contenedor.grid_columnconfigure(4, weight=2)
        contenedor.grid_columnconfigure(5, weight=1)
        contenedor.grid_columnconfigure(6, weight=2)

        ctk.CTkLabel(contenedor, text=bien["codigo_inventario"], font=FUENTES["texto_peq"],
                     text_color=COLORES["texto"], anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=8)
        ctk.CTkLabel(contenedor, text=bien["nombre"], font=FUENTES["texto_peq"],
                     text_color=COLORES["texto"], anchor="w").grid(row=0, column=1, sticky="w", padx=12)
        ctk.CTkLabel(contenedor, text=bien["tipo"], font=FUENTES["texto_peq"],
                     text_color=COLORES["texto"], anchor="w").grid(row=0, column=2, sticky="w", padx=12)
        ctk.CTkLabel(contenedor, text=bien["area"], font=FUENTES["texto_peq"],
                     text_color=COLORES["texto"], anchor="w").grid(row=0, column=3, sticky="w", padx=12)
        ctk.CTkLabel(contenedor, text=bien["responsable"], font=FUENTES["texto_peq"],
                     text_color=COLORES["texto"], anchor="w").grid(row=0, column=4, sticky="w", padx=12)

        color_estado = {
            "Activo": (COLORES["verde_claro"], COLORES["verde"]),
            "Inactivo": (COLORES["amarillo_claro"], COLORES["amarillo"]),
            "Baja": (COLORES["rojo_claro"], COLORES["rojo"]),
        }.get(bien["estado"], (COLORES["borde"], COLORES["texto_claro"]))

        badge = ctk.CTkLabel(contenedor, text=bien["estado"], font=("Segoe UI", 10, "bold"),
                              text_color=color_estado[1], fg_color=color_estado[0],
                              corner_radius=10, padx=10, pady=3)
        badge.grid(row=0, column=5, sticky="w", padx=12)

        acciones = ctk.CTkFrame(contenedor, fg_color="transparent")
        acciones.grid(row=0, column=6, sticky="w", padx=12)

        ctk.CTkButton(acciones, text="👁", width=32, height=28, font=("Segoe UI", 14),
                       fg_color="transparent", hover_color=COLORES["azul_claro"],
                       text_color=COLORES["azul_activo"],
                       command=lambda b=bien: self._ver_detalle(b)).pack(side="left", padx=2)
        ctk.CTkButton(acciones, text="✏", width=32, height=28, font=("Segoe UI", 14),
                       fg_color="transparent", hover_color=COLORES["amarillo_claro"],
                       text_color=COLORES["amarillo"],
                       command=lambda b=bien: self._editar(b)).pack(side="left", padx=2)
        ctk.CTkButton(acciones, text="🗑", width=32, height=28, font=("Segoe UI", 14),
                       fg_color="transparent", hover_color=COLORES["rojo_claro"],
                       text_color=COLORES["rojo"],
                       command=lambda b=bien: self._eliminar(b)).pack(side="left", padx=2)

    def _limpiar(self):
        self.entry_busqueda.delete(0, "end")
        self.combo_tipo.set("Todos")
        self.combo_area.set("Todos")
        self.combo_responsable.set("Todos")
        self.combo_estado.set("Todos")
        self._buscar()

    def _ver_detalle(self, bien):
        messagebox.showinfo(
            f"Detalle — {bien['codigo_inventario']}",
            f"Nombre: {bien['nombre']}\n"
            f"Descripción: {bien['descripcion'] or '(sin descripción)'}\n"
            f"Tipo: {bien['tipo']}\n"
            f"Área: {bien['area']}\n"
            f"Ubicación: {bien['ubicacion'] or '(sin ubicación)'}\n"
            f"Responsable: {bien['responsable']}\n"
            f"Fecha de adquisición: {bien['fecha_adquisicion']}\n"
            f"Valor: ${bien['valor_adquisicion']}\n"
            f"Estado: {bien['estado']}"
        )

    def _editar(self, bien):
        messagebox.showinfo("Editar", f"Edición de '{bien['nombre']}' aún no implementada.\n\nLa verás en el módulo de Alta.")

    def _eliminar(self, bien):
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el bien {bien['codigo_inventario']} — {bien['nombre']}?\n\nEsta acción no se puede deshacer."
        ):
            return

        resp = json.loads(self.cnn.ejecutar_consulta(
            "DELETE FROM bienes WHERE id_bien = %s", (bien["id_bien"],)
        ))
        if resp.get("estado"):
            messagebox.showinfo("Eliminado", "Bien eliminado correctamente.")
            self._buscar()
        else:
            messagebox.showerror(
                "Error",
                f"No se pudo eliminar:\n{resp.get('error', '')}\n\n"
                "Verifique que no tenga movimientos, conciliaciones o registros contables asociados."
            )