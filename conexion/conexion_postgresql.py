import psycopg2
import json
from config import DB_CONFIG


class ConexionPostgresql:

    NOMBRE_MOTOR = "PostgreSQL"
    PARAM = "%s"

    def __init__(self):
        self.CNX = None
        self.CURSOR = None

    def crear_conexion(self):
        try:
            self.CNX = psycopg2.connect(
                host=DB_CONFIG["host"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=DB_CONFIG["port"],
                connect_timeout=5
            )
            self.CURSOR = self.CNX.cursor()
            return self.CNX
        except Exception as e:
            print(f"Error al conectar: {e}")
            self.CNX = None
            self.CURSOR = None
            return None

    def ejecutar_consulta(self, sql, parametros=None):
        try:
            if self.CNX is None or self.CNX.closed != 0:
                if self.crear_conexion() is None:
                    return json.dumps(
                        {"estado": False, "tipo": "ConexionError", "mensaje": "No fue posible conectarse"},
                        ensure_ascii=False
                    )
            if parametros:
                self.CURSOR.execute(sql, parametros)
            else:
                self.CURSOR.execute(sql)

            tipo = sql.strip().split()[0].upper()

            if tipo == "SELECT":
                columnas = [c[0] for c in self.CURSOR.description]
                registros = self.CURSOR.fetchall()
                resultado = [dict(zip(columnas, r)) for r in registros]
                return json.dumps(
                    {"estado": True, "tipo": "SELECT", "registros": resultado},
                    ensure_ascii=False, default=str
                )

            filas = self.CURSOR.rowcount
            self.CNX.commit()
            return json.dumps(
                {"estado": True, "tipo": tipo, "filas_afectadas": filas},
                ensure_ascii=False
            )

        except psycopg2.IntegrityError as e:
            self._rollback()
            return json.dumps(
                {"estado": False, "tipo": "IntegrityError", "codigo": e.pgcode, "error": str(e)},
                ensure_ascii=False
            )
        except psycopg2.ProgrammingError as e:
            self._rollback()
            return json.dumps(
                {"estado": False, "tipo": "ProgrammingError", "codigo": e.pgcode, "error": str(e)},
                ensure_ascii=False
            )
        except psycopg2.OperationalError as e:
            self._rollback()
            self.CNX = None
            self.CURSOR = None
            return json.dumps(
                {"estado": False, "tipo": "OperationalError", "codigo": e.pgcode, "error": str(e)},
                ensure_ascii=False
            )
        except psycopg2.Error as e:
            self._rollback()
            return json.dumps(
                {"estado": False, "tipo": "DatabaseError", "codigo": e.pgcode, "error": str(e)},
                ensure_ascii=False
            )
        except Exception as e:
            self._rollback()
            return json.dumps(
                {"estado": False, "tipo": "Error", "error": str(e)},
                ensure_ascii=False
            )

    def _rollback(self):
        if self.CNX:
            try:
                self.CNX.rollback()
            except Exception:
                pass

    def cerrar_conexion(self):
        try:
            if self.CURSOR:
                self.CURSOR.close()
                self.CURSOR = None
            if self.CNX and self.CNX.closed == 0:
                self.CNX.close()
                self.CNX = None
            return True
        except Exception:
            return False