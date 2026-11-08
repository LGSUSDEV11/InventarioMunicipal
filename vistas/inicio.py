import json
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from componentes.tema import COLORES, FUENTES
from componentes.tarjeta import TarjetaEstadistica
from repositorios.repo_bienes import RepoBienes

plt.rcParams['text.color'] = COLORES["texto"]
plt.rcParams['axes.labelcolor'] = COLORES["texto_claro"]
plt.rcParams['xtick.color'] = COLORES["texto_claro"]
plt.rcParams['ytick.color'] = COLORES["texto_claro"]

class VistaInicio(ctk.CTkFrame):

    def __init__(self, master, cnn_sql): # <-- Recibe cnn_sql
        super().__init__(master, fg_color=COLORES["fondo"], corner_radius=0)
        self.cnn = cnn_sql
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="Bienvenido(a), María López García",
                     font=FUENTES["titulo"], text_color=COLORES["texto"]).pack(
            anchor="w", padx=30, pady=(25, 0))
        ctk.CTkLabel(self, text="Departamento de Tesorería (Datos desde SQL Server)",
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

        fila_graficas = ctk.CTkFrame(self, fg_color="transparent")
        fila_graficas.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        fila_graficas.grid_columnconfigure(0, weight=2)
        fila_graficas.grid_columnconfigure(1, weight=1)

        self._crear_grafica_lineas(fila_graficas)
        self._crear_grafica_dona(fila_graficas)

    def _crear_grafica_lineas(self, master):
        marco = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                              border_width=1, border_color=COLORES["borde"])
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(marco, text="Bienes adquiridos por mes", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 0))

        # Usa la consulta de SQL Server
        sql = RepoBienes.SQL_GRAFICA_MES
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        datos = resp.get("registros", [])
        
        meses = [d["mes"] for d in datos]
        totales = [d["total"] for d in datos]

        if not meses:
            meses = ["2024-01", "2024-02"]
            totales = [0, 0]

        fig = Figure(figsize=(5, 3), dpi=100, facecolor=COLORES["blanco"])
        ax = fig.add_subplot(111)
        ax.plot(meses, totales, marker='o', color="#2563eb", linewidth=2, markersize=6)
        ax.fill_between(meses, totales, color="#dbeafe", alpha=0.5)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e5e7eb')
        ax.spines['bottom'].set_color('#e5e7eb')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        canvas = FigureCanvasTkAgg(fig, master=marco)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _crear_grafica_dona(self, master):
        marco = ctk.CTkFrame(master, fg_color=COLORES["blanco"], corner_radius=12,
                              border_width=1, border_color=COLORES["borde"])
        marco.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(marco, text="Distribución por estado", font=FUENTES["subtitulo"],
                     text_color=COLORES["texto"]).pack(anchor="w", padx=20, pady=(15, 0))

        sql = RepoBienes.SQL_GRAFICA_ESTADO
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        datos = resp.get("registros", [])

        etiquetas = [d["estado"] for d in datos]
        valores = [d["total"] for d in datos]

        if not etiquetas:
            etiquetas = ["Sin datos"]
            valores = [1]

        colores_dona = []
        for e in etiquetas:
            if e == "Activo": colores_dona.append("#10b981")
            elif e == "Inactivo": colores_dona.append("#f59e0b")
            elif e == "Baja": colores_dona.append("#ef4444")
            else: colores_dona.append("#cbd5e1")

        fig = Figure(figsize=(3, 3), dpi=100, facecolor=COLORES["blanco"])
        ax = fig.add_subplot(111)
        ax.pie(valores, labels=etiquetas, colors=colores_dona, autopct='%1.0f%%',
               startangle=90, wedgeprops=dict(width=0.4, edgecolor='w'))
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=marco)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _obtener_estadisticas(self):
        sql = RepoBienes.SQL_STATS
        resp = json.loads(self.cnn.ejecutar_consulta(sql))
        if not resp.get("estado") or not resp["registros"]:
            return {"total": 0, "activos": 0, "mantenimiento": 0, "bajas": 0,
                    "nuevos": 0, "porc_activos": 0, "porc_mant": 0, "porc_bajas": 0}
        r = resp["registros"][0]
        total = r["total"] or 1
        return {
            "total": r["total"],
            "activos": r["activos"] or 0,
            "mantenimiento": r["mantenimiento"] or 0,
            "bajas": r["bajas"] or 0,
            "nuevos": 0,
            "porc_activos": round(100 * (r["activos"] or 0) / total, 1),
            "porc_mant": round(100 * (r["mantenimiento"] or 0) / total, 1),
            "porc_bajas": round(100 * (r["bajas"] or 0) / total, 1),
        }