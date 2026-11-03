import mssql_python
import json
import os
from dotenv import load_dotenv

load_dotenv()


class ConexionSqlServer:

    NOMBRE_MOTOR = "SQL Server"
    PARAM = "?"  # Marcador de parámetros de mssql_python

    def __init__(self):
        # Se aceptan los nombres con prefijo MSSQL_ o los nombres simples
        self.SERVER = os.environ.get("MSSQL_SERVER_NAME") or os.environ.get("SERVER_NAME")
        self.DATABASE_NAME = os.environ.get("MSSQL_DATABASE_NAME") or os.environ.get("DATABASE_NAME")
        self.USER = os.environ.get("MSSQL_USER") or os.environ.get("USER")
        self.PASSWORD = os.environ.get("MSSQL_PASSWORD") or os.environ.get("PASSWORD")
        self.PORT = os.environ.get("MSSQL_PORT") or os.environ.get("PORT")  # Opcional

        self.CNX = None
        self.CURSOR = None

    def crear_conexion(self):
        try:
            servidor = self.SERVER
            if self.PORT and servidor and "," not in servidor and "\\" not in servidor:
                servidor = f"{servidor},{self.PORT}"
            cadena_conexion = (
                f"Server={servidor};"
                f"Database={self.DATABASE_NAME};"
                f"UID={self.USER};"
                f"PWD={self.PASSWORD};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
            )
            self.CNX = mssql_python.connect(cadena_conexion, timeout=5)
            self.CURSOR = self.CNX.cursor()
            print(f"Conectado al servidor SQL Server: {self.SERVER}")
            return self.CNX
        except Exception as e:
            print(f"Error al conectarse al servidor SQL Server {self.SERVER}")
            print(e)
            self.CNX = None
            self.CURSOR = None
            return None

    def ejecutar_consulta(self, sql, parametros=None):
        try:
            if self.CNX is None:
                if self.crear_conexion() is None:
                    return json.dumps(
                        {
                            "estado": False,
                            "tipo": "ConexionError",
                            "mensaje": "No fue posible establecer la conexión a SQL Server"
                        },
                        ensure_ascii=False
                    )

            if parametros:
                self.CURSOR.execute(sql, parametros)
            else:
                self.CURSOR.execute(sql)

            tipo = sql.strip().split()[0].upper()
            
            if tipo == "SELECT":
                columnas = []
                for columna in self.CURSOR.description:
                    columnas.append(columna[0])

                registros = self.CURSOR.fetchall()
                resultado = []
                for registro in registros:
                    fila = {}
                    for i, valor in enumerate(registro):
                        fila[columnas[i]] = valor
                    resultado.append(fila)

                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "SELECT",
                        "registros": resultado
                    },
                    default=str,
                    ensure_ascii=False
                )
            
            elif tipo in ("INSERT", "UPDATE", "DELETE"):
                filas = self.CURSOR.rowcount
                self.CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "mensaje": f"Operación {tipo} ejecutada correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
            
            else:
                filas = self.CURSOR.rowcount
                self.CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "mensaje": "Consulta ejecutada correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )

        except mssql_python.IntegrityError as e:
            self._rollback()
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "IntegrityError",
                    "mensaje": "Violación de integridad en la base de datos",
                    "error": str(e)
                },
                ensure_ascii=False
            )
        except mssql_python.ProgrammingError as e:
            self._rollback()
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "ProgrammingError",
                    "mensaje": "Error en la consulta SQL",
                    "error": str(e)
                },
                ensure_ascii=False
            )
        except mssql_python.OperationalError as e:
            self._rollback()
            self.CNX = None
            self.CURSOR = None
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "OperationalError",
                    "mensaje": "Error de conexión con la base de datos",
                    "error": str(e)
                },
                ensure_ascii=False
            )
        except Exception as e:
            self._rollback()
            return json.dumps(
                {
                    "estado": False,
                    "tipo": "Error",
                    "mensaje": "Error inesperado",
                    "error": str(e)
                },
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
            if self.CNX:
                self.CNX.close()
                self.CNX = None
            print(f"Se ha cerrado la conexión con el servidor SQL Server: {self.SERVER}")
            return True
        except Exception as e:
            print("Error al desconectarse de SQL Server")
            print(e)
            return False