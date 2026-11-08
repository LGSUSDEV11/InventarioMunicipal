class RepoDashboard:
    # Consultas de conciliación
    PG_CONCILIACION = """
        SELECT b.id_bien, b.codigo_inventario, b.nombre, b.valor_adquisicion,
               b.estado, rc.valor_contable
        FROM bienes b
        LEFT JOIN registros_contables rc ON rc.id_bien = b.id_bien AND rc.fecha_registro BETWEEN %s AND %s
        JOIN ubicaciones u ON u.id_ubicacion = b.id_ubicacion
        JOIN areas a ON a.id_area = u.id_area
        WHERE 1=1
    """
    
    # Consultas de reportes
    PG_REPORTES = """
        SELECT b.codigo_inventario, b.nombre, b.fecha_adquisicion, b.valor_adquisicion,
               b.estado, t.nombre AS tipo, a.nombre AS area, r.nombre AS responsable
        FROM bienes b
        JOIN tipos_bien t ON t.id_tipo = b.id_tipo
        JOIN ubicaciones u ON u.id_ubicacion = b.id_ubicacion
        JOIN areas a ON a.id_area = u.id_area
        JOIN responsables r ON r.id_responsable = b.id_responsable
        WHERE b.fecha_adquisicion BETWEEN %s AND %s
    """