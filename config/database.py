"""
Configuración de conexiones a bases de datos
Metaltronic S.A. - Pipeline de Datos
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymongo
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConfig:
    """Clase para manejar configuraciones de base de datos"""
    
    def __init__(self):
        # Configuración PostgreSQL
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'user': os.getenv('POSTGRES_USER', 'metaltronic_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'metaltronic_pass'),
            'database': os.getenv('POSTGRES_DB', 'metaltronic_db')
        }
        
        # Configuración MongoDB
        self.mongo_config = {
            'host': os.getenv('MONGO_HOST', 'mongodb'),
            'port': os.getenv('MONGO_PORT', '27017'),
            'user': os.getenv('MONGO_USER', 'mongo_user'),
            'password': os.getenv('MONGO_PASSWORD', 'mongo_pass'),
            'database': os.getenv('MONGO_DB', 'metaltronic_mongo')
        }
    
    def get_postgres_engine(self):
        """Crear conexión SQLAlchemy para PostgreSQL"""
        connection_string = (
            f"postgresql://{self.postgres_config['user']}:"
            f"{self.postgres_config['password']}@"
            f"{self.postgres_config['host']}:"
            f"{self.postgres_config['port']}/"
            f"{self.postgres_config['database']}"
        )
        return create_engine(connection_string)
    
    def get_postgres_session(self):
        """Crear sesión de PostgreSQL"""
        engine = self.get_postgres_engine()
        Session = sessionmaker(bind=engine)
        return Session()
    
    def get_mongo_client(self):
        """Crear cliente MongoDB"""
        connection_string = (
            f"mongodb://{self.mongo_config['user']}:"
            f"{self.mongo_config['password']}@"
            f"{self.mongo_config['host']}:"
            f"{self.mongo_config['port']}/"
        )
        return pymongo.MongoClient(connection_string)
    
    def get_mongo_database(self):
        """Obtener base de datos MongoDB"""
        client = self.get_mongo_client()
        return client[self.mongo_config['database']]

# Instancia global de configuración
db_config = DatabaseConfig()
