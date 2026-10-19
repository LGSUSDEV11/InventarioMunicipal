import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("PG_HOST") or os.environ.get("HOST") or "localhost",
    "port": int(os.environ.get("PG_PORT") or os.environ.get("PORT") or 5432),
    "database": os.environ.get("PG_DATABASE_NAME") or os.environ.get("DATABASE_NAME") or "InventarioMunicipal",
    "user": os.environ.get("PG_USER") or os.environ.get("USER"),
    "password": os.environ.get("PG_PASSWORD") or os.environ.get("PASSWORD"),
}

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")