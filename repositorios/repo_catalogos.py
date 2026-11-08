class RepoCatalogos:
    PG_TIPOS = "SELECT id_tipo AS id, nombre FROM tipos_bien ORDER BY nombre"
    PG_AREAS = "SELECT id_area AS id, nombre FROM areas WHERE estado = 'Activo' ORDER BY nombre"
    PG_RESPONSABLES = "SELECT id_responsable AS id, nombre FROM responsables WHERE estado = 'Activo' ORDER BY nombre"
    PG_UBICACIONES = """
        SELECT u.id_ubicacion AS id, 
               e.nombre || ' - ' || a.nombre AS nombre 
        FROM ubicaciones u
        JOIN edificios e ON e.id_edificio = u.id_edificio
        JOIN areas a ON a.id_area = u.id_area
        ORDER BY e.nombre
    """
    
    PG_BIENES = "SELECT id_bien AS id, codigo_inventario || ' - ' || nombre AS nombre FROM bienes ORDER BY codigo_inventario"
    PG_USUARIOS = "SELECT id_usuario AS id, usuario FROM usuarios ORDER BY usuario"