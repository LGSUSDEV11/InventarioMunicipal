import json
from tkinter import messagebox
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES
from componentes.tabla import Tabla


class VistaConfiguracion(ctk.CTkFrame):

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn

        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="⚙️  Configuración", font=FUENTES["titulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Administración de catálogos maestros del sistema.",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30, pady=(0, 15))

        self.tabs = ctk.CTkTabview(
            self,
            fg_color=COLORES["blanco"],
            segmented_button_selected_color=COLORES["azul_boton"],
            segmented_button_selected_hover_color=COLORES["azul_boton_hover"],
            segmented_button_unselected_color=COLORES["blanco"],
            segmented_button_unselected_hover_color=COLORES["fondo"],
            text_color=COLORES["texto"],
        )
        self.tabs.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.tabs.add("Tipos de bien")
        self.tabs.add("Áreas")
        self.tabs.add("Edificios")
        self.tabs.add("Cargos")

        self._crear_catalogo(
            self.tabs.tab("Tipos de bien"),
            tabla="tipos_bien",
            id_col="id_tipo",
            id_seq="tipos_bien_id_tipo_seq",
            campos=[
                ("nombre", "Nombre", True, 100),
                ("descripcion", "Descripción", False, 255),
            ],
            tiene_estado=False,
        )

        self._crear_catalogo(
            self.tabs.tab("Áreas"),
            tabla="areas",
            id_col="id_area",
            id_seq="areas_id_area_seq",
            campos=[
                ("nombre", "Nombre", True, 100),
                ("descripcion", "Descripción", False, 255),
            ],
            tiene_estado=True,
        )

        self._crear_catalogo(
            self.tabs.tab("Edificios"),
            tabla="edificios",
            id_col="id_edificio",
            id_seq="edificios_id_edificio_seq",
            campos=[
                ("nombre", "Nombre", True, 100),
                ("direccion", "Dirección", False, 255),
                ("descripcion", "Descripción", False, 255),
            ],
            tiene_estado=True,
        )

        self._crear_catalogo(
            self.tabs.tab("Cargos"),
            tabla="cargos",
            id_col="id_cargo",
            id_seq="cargos_id_cargo_seq",
            campos=[
                ("nombre", "Nombre", True, 100),
                ("descripcion", "Descripción", False, 255),
            ],
            tiene_estado=True,
        )

    # ------------------------------------------------------------------
    def _crear_catalogo(self, master, tabla, id_col, id_seq, campos, tiene_estado):
        master.grid_columnconfigure(0, weight=3)
        master.grid_columnconfigure(1, weight=2)
        master.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: tabla
        izq = ctk.CTkFrame(master, fg_color="transparent")
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)

        contenedor_tabla = ctk.CTkFrame(izq, fg_color="transparent")
        contenedor_tabla.pack(fill="both", expand=True)

        # Panel derecho: formulario
        der = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                            border_width=1, border_color=COLORES["borde"])
        der.grid(row=0, column=1, sticky="nsew", pady=10)

        estado = {
            "tabla": tabla,
            "id_col": id_col,
            "id_seq": id_seq,
            "campos": campos,
            "tiene_estado": tiene_estado,
            "editando": None,
            "widgets": {},
            "contenedor_tabla": contenedor_tabla,
            "lbl_titulo": None,
            "btn_guardar": None,
            "btn_cancelar": None,
        }

        ctk.CTkLabel(der, text="➕  Nuevo registro", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 10))
        estado["lbl_titulo"] = der.winfo_children()[-1]

        for clave, etiqueta, obligatorio, maximo in campos:
            ctk.CTkLabel(der, text=etiqueta + (" *" if obligatorio else ""),
                         font=FUENTES["texto_peq"],
                         text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(der, height=38, font=FUENTES["texto"], corner_radius=8)
            entry.pack(fill="x", padx=20, pady=(3, 10))
            estado["widgets"][clave] = entry

        if tiene_estado:
            ctk.CTkLabel(der, text="Estado *", font=FUENTES["texto_peq"],
                         text_color=COLORES["texto_claro"]).pack(anchor="w", padx=20)
            combo = ctk.CTkComboBox(der, values=["Activo", "Inactivo"], height=38,
                                     font=FUENTES["texto"], corner_radius=8, state="readonly")
            combo.pack(fill="x", padx=20, pady=(3, 15))
            combo.set("Activo")
            estado["widgets"]["estado"] = combo

        btn_guardar = ctk.CTkButton(der, text="💾  Guardar", height=42,
                                      font=FUENTES["boton"], corner_radius=8,
                                      fg_color=COLORES["azul_boton"],
                                      hover_color=COLORES["azul_boton_hover"],
                                      command=lambda e=estado: self._guardar(e))
        btn_guardar.pack(fill="x", padx=20, pady=(5, 8))
        estado["btn_guardar"] = btn_guardar

        btn_cancelar = ctk.CTkButton(der, text="✖  Cancelar", height=36,
                                       font=FUENTES["texto"], corner_radius=8,
                                       fg_color=COLORES["blanco"], hover_color=COLORES["fondo"],
                                       text_color=COLORES["texto"], border_width=1,
                                       border_color=COLORES["borde"],
                                       command=lambda e=estado: self._limpiar_formulario(e))
        estado["btn_cancelar"] = btn_cancelar

        self.after(50, lambda e=estado: self._cargar(e))

    def _cargar(self, e):
        columnas_db = [c[0] for c in e["campos"]]
        if e["tiene_estado"]:
            columnas_db.append("estado")

        sql = f"SELECT {e['id_col']}, " + ", ".join(columnas_db) + f" FROM {e['tabla']} ORDER BY {e['id_col']}"
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado"):
            messagebox.showerror("Error", resp.get("error", "No se pudo cargar."))
            return
        registros = resp["registros"]

        for w in e["contenedor_tabla"].winfo_children():
            w.destroy()

        encabezados = [c[1] for c in e["campos"]]
        if e["tiene_estado"]:
            encabezados.append("Estado")
        encabezados.append("Acciones")

        anchos = [3] * len(e["campos"])
        if e["tiene_estado"]:
            anchos.append(2)
        anchos.append(2)

        tabla = Tabla(e["contenedor_tabla"], columnas=encabezados, anchos=anchos)
        tabla.pack(fill="both", expand=True)

        for r in registros:
            fila = ctk.CTkFrame(tabla.cuerpo, fg_color=COLORES["blanco"], corner_radius=0)
            fila.pack(fill="x")
            for i, w in enumerate(anchos):
                fila.grid_columnconfigure(i, weight=w)

            col_idx = 0
            for clave, _, _, _ in e["campos"]:
                valor = r.get(clave)
                texto = "" if valor is None else str(valor)
                ctk.CTkLabel(fila, text=texto[:60], font=FUENTES["texto_peq"],
                             text_color=COLORES["texto"], anchor="w").grid(
                    row=0, column=col_idx, sticky="w", padx=12, pady=8)
                col_idx += 1

            if e["tiene_estado"]:
                color_estado = (COLORES["verde_claro"], COLORES["verde"]) if r["estado"] == "Activo" \
                    else (COLORES["rojo_claro"], COLORES["rojo"])
                ctk.CTkLabel(fila, text=r["estado"], font=("Segoe UI", 10, "bold"),
                             text_color=color_estado[1], fg_color=color_estado[0],
                             corner_radius=10, padx=10, pady=3).grid(
                    row=0, column=col_idx, sticky="w", padx=12)
                col_idx += 1

            acciones = ctk.CTkFrame(fila, fg_color="transparent")
            acciones.grid(row=0, column=col_idx, sticky="w", padx=12)

            ctk.CTkButton(acciones, text="✏", width=30, height=26, font=("Segoe UI", 13),
                           fg_color="transparent", hover_color=COLORES["amarillo_claro"],
                           text_color=COLORES["amarillo"],
                           command=lambda reg=r, est=e: self._editar(est, reg)).pack(side="left", padx=2)
            ctk.CTkButton(acciones, text="🗑", width=30, height=26, font=("Segoe UI", 13),
                           fg_color="transparent", hover_color=COLORES["rojo_claro"],
                           text_color=COLORES["rojo"],
                           command=lambda reg=r, est=e: self._eliminar(est, reg)).pack(side="left", padx=2)

    # ------------------------------------------------------------------
    def _editar(self, e, registro):
        e["editando"] = registro
        e["lbl_titulo"].configure(text=f"✏  Editando ID {registro[e['id_col']]}")
        for clave, _, _, _ in e["campos"]:
            w = e["widgets"][clave]
            w.delete(0, "end")
            valor = registro.get(clave)
            if valor:
                w.insert(0, str(valor))
        if e["tiene_estado"]:
            e["widgets"]["estado"].set(registro["estado"])
        e["btn_guardar"].configure(text="💾  Actualizar")
        e["btn_cancelar"].pack(fill="x", padx=20, pady=(0, 20))

    def _limpiar_formulario(self, e):
        e["editando"] = None
        e["lbl_titulo"].configure(text="➕  Nuevo registro")
        for clave, _, _, _ in e["campos"]:
            e["widgets"][clave].delete(0, "end")
        if e["tiene_estado"]:
            e["widgets"]["estado"].set("Activo")
        e["btn_guardar"].configure(text="💾  Guardar")
        e["btn_cancelar"].pack_forget()

    def _guardar(self, e):
        valores = {}
        for clave, etiqueta, obligatorio, maximo in e["campos"]:
            v = e["widgets"][clave].get().strip()
            if obligatorio and not v:
                messagebox.showwarning("Faltan datos", f"El campo '{etiqueta}' es obligatorio.")
                return
            if len(v) > maximo:
                messagebox.showwarning("Muy largo", f"'{etiqueta}' excede {maximo} caracteres.")
                return
            valores[clave] = v or None

        if e["tiene_estado"]:
            valores["estado"] = e["widgets"]["estado"].get()

        if e["editando"]:
            sets = ", ".join([f"{k} = %s" for k in valores.keys()])
            sql = f"UPDATE {e['tabla']} SET {sets} WHERE {e['id_col']} = %s"
            params = tuple(valores.values()) + (e["editando"][e["id_col"]],)
        else:
            columnas = ", ".join(valores.keys())
            placeholders = ", ".join(["%s"] * len(valores))
            sql = f"INSERT INTO {e['tabla']} ({columnas}) VALUES ({placeholders})"
            params = tuple(valores.values())

        resp = json.loads(self.cnn.ejecutar_consulta(sql, params))
        if resp.get("estado"):
            messagebox.showinfo("Guardado", "Registro guardado correctamente.")
            self._limpiar_formulario(e)
            self._cargar(e)
        else:
            if resp.get("codigo") == "23505":
                messagebox.showerror("Duplicado", "Ya existe un registro con ese nombre.")
            else:
                messagebox.showerror("Error", resp.get("error", "No se pudo guardar."))

    def _eliminar(self, e, registro):
        id_val = registro[e["id_col"]]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar el registro ID {id_val}?"):
            return
        resp = json.loads(self.cnn.ejecutar_consulta(
            f"DELETE FROM {e['tabla']} WHERE {e['id_col']} = %s", (id_val,)
        ))
        if resp.get("estado"):
            messagebox.showinfo("Eliminado", "Registro eliminado.")
            self._cargar(e)
        else:
            messagebox.showerror("Error",
                "No se pudo eliminar. Puede que esté en uso por otros registros.")