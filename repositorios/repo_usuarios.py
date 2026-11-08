class RepoUsuarios:
    # PostgreSQL (%s)
    PG_BUSCAR = "SELECT id_usuario, usuario, rol, estado FROM usuarios WHERE 1=1"
    PG_INSERTAR = "INSERT INTO usuarios (usuario, password, rol, estado) VALUES (%s, %s, %s, %s)"
    PG_ACTUALIZAR_CON_PASS = "UPDATE usuarios SET password = %s, rol = %s, estado = %s WHERE id_usuario = %s"
    PG_ACTUALIZAR_SIN_PASS = "UPDATE usuarios SET rol = %s, estado = %s WHERE id_usuario = %s"
    PG_ELIMINAR = "DELETE FROM usuarios WHERE id_usuario = %s"

    # SQL Server (?)
    SQL_BUSCAR = "SELECT id_usuario, usuario, rol, estado FROM usuarios WHERE 1=1"
    SQL_INSERTAR = "INSERT INTO usuarios (usuario, password, rol, estado) VALUES (?, ?, ?, ?)"
    SQL_ACTUALIZAR_CON_PASS = "UPDATE usuarios SET password = ?, rol = ?, estado = ? WHERE id_usuario = ?"
    SQL_ACTUALIZAR_SIN_PASS = "UPDATE usuarios SET rol = ?, estado = ? WHERE id_usuario = ?"
    SQL_ELIMINAR = "DELETE FROM usuarios WHERE id_usuario = ?"
    
    # Estadísticas
    PG_STATS = """
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE estado='Activo') AS activos,
               COUNT(*) FILTER (WHERE estado='Inactivo') AS inactivos
        FROM usuarios
    """
    SQL_STATS = """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN estado='Activo' THEN 1 ELSE 0 END) AS activos,
               SUM(CASE WHEN estado='Inactivo' THEN 1 ELSE 0 END) AS inactivos
        FROM usuarios
    """