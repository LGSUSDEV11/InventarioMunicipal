# Sistema de Inventario de Bienes Patrimoniales - H. Ayuntamiento de Sahuayo

## Alumno: José de Jesús Flores Sánchez

## Descripción del Proyecto
Aplicación de escritorio desarrollada en Python para el control y conciliación del inventario de bienes patrimoniales del Ayuntamiento de Sahuayo. El sistema permite gestionar bienes, registrar movimientos, realizar conciliaciones físico-contables y generar reportes en PDF/Excel.

## Tecnologías Utilizadas
- **Lenguaje:** Python 3.12
- **Interfaz Gráfica:** CustomTkinter
- **Base de Datos:** PostgreSQL
- **Librerías principales:** `psycopg2` (conexión BD), `reportlab` (PDF), `openpyxl` (Excel), `python-dotenv` (variables de entorno).

*Nota sobre la interfaz:* Se eligió **CustomTkinter** en lugar de PyQt6 porque permitió replicar de manera más ágil y ligera el diseño institucional moderno (colores, tarjetas redondeadas, menú lateral) solicitado en las interfaces de referencia.

## Arquitectura y Estructura del Código
El proyecto sigue una arquitectura modular por componentes:
- `conexion/`: Clase encargada del manejo de la base de datos (commit, rollback, manejo de errores SQL).
- `componentes/`: Widgets reutilizables (sidebar, topbar, tablas, tarjetas, tema de colores).
- `vistas/`: Pantallas del sistema (Inicio, Bienes, Movimientos, Conciliación, Reportes, Usuarios, Configuración).
- `reportes/`: Lógica para generación de archivos PDF y Excel.
- `main.py`: Punto de entrada del sistema.

## Catálogos (Tablas Maestras)
Debido a que el dominio del sistema es el **inventario patrimonial municipal** (no un punto de venta), los catálogos que se administran en el sistema son: 
- Tipos de bien
- Áreas
- Edificios
- Cargos

*(No se incluyen Clientes o Proveedores porque no aplican a la naturaleza del Ayuntamiento).* Estos catálogos cuentan con su CRUD completo dentro del módulo de **Configuración**.

## Requisitos e Instalación

1. Tener instalado Python 3.9 o superior y PostgreSQL.
2. Clonar el repositorio o descomprimir el proyecto.
3. Crear un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
