class RepoMovimientos:
    PG_BUSCAR = """
        SELECT m.id_movimiento, m.tipo_movimiento, m.fecha_movimiento, m.descripcion,
               b.codigo_inventario, b.nombre AS bien, b.id_bien,
               u.usuario, b.estado
        FROM movimientos m
        JOIN bienes b ON b.id_bien = m.id_bien
        JOIN usuarios u ON u.id_usuario = m.id_usuario
        WHERE 1=1
    """
    PG_INSERTAR = """
        INSERT INTO movimientos (id_bien, id_usuario, tipo_movimiento, fecha_movimiento, descripcion) 
        VALUES (%s, %s, %s, %s, %s)
    """
    PG_ACTUALIZAR_RESPONSABLE = "UPDATE bienes SET id_responsable = %s WHERE id_bien = %s"
    PG_ACTUALIZAR_UBICACION = "UPDATE bienes SET id_ubicacion = %s WHERE id_bien = %s"
    PG_ACTUALIZAR_ESTADO = "UPDATE bienes SET estado = %s WHERE id_bien = %s"