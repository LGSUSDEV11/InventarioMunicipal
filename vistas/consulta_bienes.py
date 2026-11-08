import json
import customtkinter as ctk
from tkinter import messagebox
from componentes.tema import COLORES, FUENTES
from componentes.tabla import Tabla
from repositorios.repo_bienes import RepoBienes # <-- IMPORTAMOS
from repositorios.repo_catalogos import RepoCatalogos # <-- IMPORTAMOS

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
        # ... (Igual hasta los filtros) ...
        ctk.CTkLabel(self, text="🔍  Consulta de bienes",
                     font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(25, 0))
        # ... (todo el diseño de filtros se queda exactamente igual) ...
        # (Copia tu método _construir, _combo_filtro, _traer_catalogo tal cual están)
        pass

    def _cargar_catalogos(self):
        # Usamos el repositorio de catálogos
        self.catalogos["tipos"] = self._traer_catalogo(RepoCatalogos.PG_TIPOS)
        self.catalogos["areas"] = self._traer_catalogo(RepoCatalogos.PG_AREAS)
        self.catalogos["responsables"] = self._traer_catalogo(RepoCatalogos.PG_RESPONSABLES)

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
        sql = RepoBienes.PG_LISTAR # <-- USAMOS EL REPO
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

    # ... (Los métodos _renderizar, _agregar_fila, _limpiar, _ver_detalle se quedan igual) ...

    def _eliminar(self, bien):
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el bien {bien['codigo_inventario']} — {bien['nombre']}?\n\nEsta acción no se puede deshacer."
        ):
            return

        # Usamos el repositorio
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