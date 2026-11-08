class RepoBienes:
    # Listado principal (usado en consulta_bienes y dashboard)
    PG_LISTAR = """
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
    
    # Inserción
    PG_INSERTAR = """
        INSERT INTO bienes (codigo_inventario, nombre, descripcion, fecha_adquisicion, valor_adquisicion, estado, id_tipo, id_ubicacion, id_responsable) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_bien
    """
    
    # Dashboard
    PG_STATS = """
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE estado = 'Activo') AS activos,
               COUNT(*) FILTER (WHERE estado = 'Inactivo') AS mantenimiento,
               COUNT(*) FILTER (WHERE estado = 'Baja') AS bajas
        FROM bienes
    """
    PG_GRAFICA_MES = """
        SELECT TO_CHAR(fecha_adquisicion, 'YYYY-MM') AS mes, COUNT(*) AS total
        FROM bienes GROUP BY TO_CHAR(fecha_adquisicion, 'YYYY-MM') ORDER BY mes
    """
    PG_GRAFICA_ESTADO = "SELECT estado, COUNT(*) AS total FROM bienes GROUP BY estado"

    # SQL Server
    SQL_LISTAR = PG_LISTAR.replace('%s', '?')
    SQL_INSERTAR = PG_INSERTAR.replace('%s', '?').replace(' RETURNING id_bien', '')

        # Agrega esto DENTRO de la clase RepoBienes:
    SQL_STATS = """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) AS activos,
               SUM(CASE WHEN estado = 'Inactivo' THEN 1 ELSE 0 END) AS mantenimiento,
               SUM(CASE WHEN estado = 'Baja' THEN 1 ELSE 0 END) AS bajas
        FROM bienes
    """
    SQL_GRAFICA_MES = """
        SELECT FORMAT(fecha_adquisicion, 'yyyy-MM') AS mes, COUNT(*) AS total
        FROM bienes GROUP BY FORMAT(fecha_adquisicion, 'yyyy-MM') ORDER BY mes
    """
    SQL_GRAFICA_ESTADO = "SELECT estado, COUNT(*) AS total FROM bienes GROUP BY estado"