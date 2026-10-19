import json
import customtkinter as ctk
from componentes.tema import COLORES, FUENTES
from componentes.tarjeta import TarjetaEstadistica
from componentes.tabla import Tabla


class VistaInicio(ctk.CTkFrame):

    def __init__(self, master, cnn):
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="Bienvenido(a), María López García",
                     font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Departamento de Tesorería",
                     font=FUENTES["texto"], text_color=COLORES["texto_claro"]).pack(
            anchor="w", padx=30)

        stats = self._obtener_estadisticas()

        fila_stats = ctk.CTkFrame(self, fg_color="transparent")
        fila_stats.pack(fill="x", padx=30, pady=25)
        for i in range(4):
            fila_stats.grid_columnconfigure(i, weight=1)

        tarjetas = [
            ("Total de bienes", stats["total"], "📦", COLORES["azul_activo"],
             f"+{stats['nuevos']} este mes", COLORES["verde"]),
            ("Bienes en uso", stats["activos"], "🖥️", COLORES["azul_activo"],
             f"{stats['porc_activos']}% del total", COLORES["texto_claro"]),
            ("Bienes en mantenimiento", stats["mantenimiento"], "🔧", COLORES["amarillo"],
             f"{stats['porc_mant']}% del total", COLORES["texto_claro"]),
            ("Bienes dados de baja", stats["bajas"], "⚠️", COLORES["rojo"],
             f"{stats['porc_bajas']}% del total", COLORES["texto_claro"]),
        ]

        for i, (titulo, valor, icono, color, sub, color_sub) in enumerate(tarjetas):
            t = TarjetaEstadistica(fila_stats, titulo, valor, icono, color, sub, color_sub)
            t.grid(row=0, column=i, padx=8, sticky="nsew")

        ctk.CTkLabel(self, text="Listado de bienes",
                     font=FUENTES["subtitulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(15, 10))

        tabla = Tabla(
            self,
            columnas=["No. Inventario", "Descripción", "Departamento", "Responsable", "Estado"],
            anchos=[2, 4, 2, 3, 2]
        )
        tabla.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        tabla.cargar(self._obtener_bienes())

    def _obtener_estadisticas(self):
        sql = """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE estado = 'Activo') AS activos,
                COUNT(*) FILTER (WHERE estado = 'Inactivo') AS mantenimiento,
                COUNT(*) FILTER (WHERE estado = 'Baja') AS bajas
            FROM bienes
        """
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado") or not resp["registros"]:
            return {"total": 0, "activos": 0, "mantenimiento": 0, "bajas": 0,
                    "nuevos": 0, "porc_activos": 0, "porc_mant": 0, "porc_bajas": 0}
        r = resp["registros"][0]
        total = r["total"] or 1
        return {
            "total": r["total"],
            "activos": r["activos"],
            "mantenimiento": r["mantenimiento"],
            "bajas": r["bajas"],
            "nuevos": 0,
            "porc_activos": round(100 * r["activos"] / total, 1),
            "porc_mant": round(100 * r["mantenimiento"] / total, 1),
            "porc_bajas": round(100 * r["bajas"] / total, 1),
        }

    def _obtener_bienes(self):
        sql = """
            SELECT b.codigo_inventario, b.nombre, a.nombre AS area,
                   r.nombre AS responsable, b.estado
            FROM bienes b
            JOIN ubicaciones u ON u.id_ubicacion = b.id_ubicacion
            JOIN areas a ON a.id_area = u.id_area
            JOIN responsables r ON r.id_responsable = b.id_responsable
            ORDER BY b.id_bien
            LIMIT 20
        """
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado"):
            return []
        return [[r["codigo_inventario"], r["nombre"], r["area"],
                 r["responsable"], r["estado"]] for r in resp["registros"]]