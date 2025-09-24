"""
Módulo de Extracción de Datos
Metaltronic S.A. - Pipeline ETL
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from config.database import db_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractor:
    """Clase para extraer datos de diferentes fuentes"""
    
    def __init__(self):
        self.db_config = db_config
    
    def extract_sales_data(self, fecha_inicio=None, fecha_fin=None):
        """
        Extraer datos de ventas desde PostgreSQL
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'
            fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'
        
        Returns:
            pd.DataFrame: DataFrame con datos de ventas
        """
        try:
            # Si no se especifica fecha, usar último día
            if not fecha_inicio:
                fecha_inicio = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            if not fecha_fin:
                fecha_fin = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Extrayendo datos de ventas desde {fecha_inicio} hasta {fecha_fin}")
            
            # Query SQL para extraer datos de ventas con joins
            query = """
            SELECT 
                t.id_transaccion,
                t.numero_factura,
                t.fecha_venta,
                c.nombre_cliente,
                c.ciudad,
                c.provincia,
                p.codigo_producto,
                p.nombre_producto,
                p.categoria,
                p.material,
                dv.cantidad,
                dv.precio_unitario,
                dv.descuento,
                dv.subtotal,
                t.total as total_factura,
                t.metodo_pago,
                t.vendedor,
                t.sucursal
            FROM ventas.transacciones t
            JOIN ventas.clientes c ON t.id_cliente = c.id_cliente
            JOIN ventas.detalle_ventas dv ON t.id_transaccion = dv.id_transaccion
            JOIN inventario.productos p ON dv.id_producto = p.id_producto
            WHERE t.fecha_venta BETWEEN %s AND %s
            ORDER BY t.fecha_venta, t.id_transaccion
            """
            
            # Ejecutar consulta
            engine = self.db_config.get_postgres_engine()
            df = pd.read_sql_query(query, engine, params=[fecha_inicio, fecha_fin])
            
            logger.info(f"Extraídos {len(df)} registros de ventas")
            return df
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de ventas: {str(e)}")
            raise
    
    def extract_inventory_data(self):
        """
        Extraer datos de inventario desde PostgreSQL
        
        Returns:
            pd.DataFrame: DataFrame con datos de inventario
        """
        try:
            logger.info("Extrayendo datos de inventario")
            
            query = """
            SELECT 
                id_producto,
                codigo_producto,
                nombre_producto,
                categoria,
                material,
                peso_kg,
                precio_unitario,
                stock_actual,
                stock_minimo,
                CASE 
                    WHEN stock_actual <= stock_minimo THEN 'BAJO'
                    WHEN stock_actual <= stock_minimo * 2 THEN 'MEDIO'
                    ELSE 'ALTO'
                END as nivel_stock,
                fecha_creacion,
                activo
            FROM inventario.productos
            WHERE activo = true
            ORDER BY categoria, codigo_producto
            """
            
            engine = self.db_config.get_postgres_engine()
            df = pd.read_sql_query(query, engine)
            
            logger.info(f"Extraídos {len(df)} productos del inventario")
            return df
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de inventario: {str(e)}")
            raise
    
    def extract_logs_data(self, fecha_inicio=None, fecha_fin=None):
        """
        Extraer datos de logs desde MongoDB
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'
            fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'
        
        Returns:
            pd.DataFrame: DataFrame con datos de logs
        """
        try:
            # Si no se especifica fecha, usar último día
            if not fecha_inicio:
                fecha_inicio = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            if not fecha_fin:
                fecha_fin = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Extrayendo logs desde {fecha_inicio} hasta {fecha_fin}")
            
            # Conectar a MongoDB
            db = self.db_config.get_mongo_database()
            collection = db['logs_ventas']
            
            # Crear filtro de fechas
            start_date = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            end_date = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
            
            # Query MongoDB
            cursor = collection.find({
                'timestamp': {
                    '$gte': start_date,
                    '$lt': end_date
                }
            })
            
            # Convertir a DataFrame
            logs_data = list(cursor)
            if logs_data:
                df = pd.json_normalize(logs_data)
                logger.info(f"Extraídos {len(df)} registros de logs")
                return df
            else:
                logger.info("No se encontraron logs para el período especificado")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error extrayendo datos de logs: {str(e)}")
            raise
    
    def extract_all_data(self, fecha_inicio=None, fecha_fin=None):
        """
        Extraer todos los datos necesarios para el ETL
        
        Args:
            fecha_inicio (str): Fecha de inicio
            fecha_fin (str): Fecha de fin
        
        Returns:
            dict: Diccionario con todos los DataFrames
        """
        try:
            logger.info("Iniciando extracción completa de datos")
            
            data = {
                'ventas': self.extract_sales_data(fecha_inicio, fecha_fin),
                'inventario': self.extract_inventory_data(),
                'logs': self.extract_logs_data(fecha_inicio, fecha_fin)
            }
            
            logger.info("Extracción completa finalizada")
            return data
            
        except Exception as e:
            logger.error(f"Error en extracción completa: {str(e)}")
            raise

# Función helper para Airflow
def extract_data_task(**context):
    """Task function para Airflow"""
    extractor = DataExtractor()
    fecha_ejecucion = context['ds']  # Fecha de ejecución del DAG
    
    # Extraer datos
    data = extractor.extract_all_data(fecha_ejecucion, fecha_ejecucion)
    
    # Guardar datos en archivos temporales (simular S3)
    import os
    os.makedirs('/opt/airflow/data/raw', exist_ok=True)
    
    for key, df in data.items():
        if not df.empty:
            file_path = f'/opt/airflow/data/raw/{key}_{fecha_ejecucion}.csv'
            df.to_csv(file_path, index=False)
            logger.info(f"Datos de {key} guardados en {file_path}")
    
    return "Extracción completada"
