"""
Módulo de Carga de Datos
Metaltronic S.A. - Pipeline ETL
"""

import pandas as pd
import logging
from sqlalchemy import text
from config.database import db_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Clase para cargar datos transformados a destinos finales"""
    
    def __init__(self):
        self.db_config = db_config
    
    def load_daily_summary(self, df_resumen):
        """
        Cargar resumen diario a PostgreSQL
        
        Args:
            df_resumen (pd.DataFrame): DataFrame con resumen diario
        """
        try:
            logger.info("Cargando resumen diario a PostgreSQL")
            
            if df_resumen.empty:
                logger.warning("DataFrame de resumen diario está vacío")
                return
            
            # Obtener conexión
            engine = self.db_config.get_postgres_engine()
            
            # Limpiar datos existentes para las fechas a cargar
            fechas_a_cargar = df_resumen['fecha_resumen'].unique()
            
            with engine.connect() as conn:
                for fecha in fechas_a_cargar:
                    delete_query = text(
                        "DELETE FROM analytics.resumen_ventas_diario WHERE fecha_resumen = :fecha"
                    )
                    conn.execute(delete_query, {"fecha": fecha})
                conn.commit()
                logger.info(f"Eliminados registros existentes para {len(fechas_a_cargar)} fechas")
            
            # Preparar datos para inserción
            df_to_load = df_resumen[[
                'fecha_resumen', 'total_ventas', 'total_transacciones', 
                'productos_vendidos', 'cliente_mas_frecuente', 
                'categoria_mas_vendida', 'promedio_ticket'
            ]].copy()
            
            # Cargar datos nuevos
            df_to_load.to_sql(
                name='resumen_ventas_diario',
                schema='analytics',
                con=engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            
            logger.info(f"Cargados {len(df_to_load)} registros de resumen diario")
            
        except Exception as e:
            logger.error(f"Error cargando resumen diario: {str(e)}")
            raise
    
    def load_inventory_analysis(self, df_analisis):
        """
        Cargar análisis de inventario a PostgreSQL
        
        Args:
            df_analisis (pd.DataFrame): DataFrame con análisis de inventario
        """
        try:
            logger.info("Cargando análisis de inventario a PostgreSQL")
            
            if df_analisis.empty:
                logger.warning("DataFrame de análisis de inventario está vacío")
                return
            
            # Crear tabla si no existe
            engine = self.db_config.get_postgres_engine()
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS analytics.analisis_inventario (
                codigo_producto VARCHAR(20) PRIMARY KEY,
                nombre_producto VARCHAR(200),
                categoria VARCHAR(50),
                stock_actual INTEGER,
                cantidad_vendida INTEGER,
                ingresos_producto DECIMAL(12,2),
                rotacion_inventario DECIMAL(8,4),
                dias_stock DECIMAL(8,2),
                performance VARCHAR(20),
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            with engine.connect() as conn:
                conn.execute(text(create_table_query))
                conn.commit()
            
            # Limpiar tabla existente
            with engine.connect() as conn:
                conn.execute(text("TRUNCATE TABLE analytics.analisis_inventario"))
                conn.commit()
            
            # Preparar datos para carga
            df_to_load = df_analisis[[
                'codigo_producto', 'nombre_producto', 'categoria',
                'stock_actual', 'cantidad_vendida', 'ingresos_producto',
                'rotacion_inventario', 'dias_stock', 'performance'
            ]].copy()
            
            # Limpiar valores infinitos
            df_to_load['dias_stock'] = df_to_load['dias_stock'].replace([float('inf')], 999)
            
            # Cargar datos
            df_to_load.to_sql(
                name='analisis_inventario',
                schema='analytics',
                con=engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            
            logger.info(f"Cargados {len(df_to_load)} registros de análisis de inventario")
            
        except Exception as e:
            logger.error(f"Error cargando análisis de inventario: {str(e)}")
            raise
    
    def load_logs_summary(self, df_logs):
        """
        Cargar resumen de logs a MongoDB
        
        Args:
            df_logs (pd.DataFrame): DataFrame con logs procesados
        """
        try:
            logger.info("Cargando resumen de logs a MongoDB")
            
            if df_logs.empty:
                logger.warning("DataFrame de logs está vacío")
                return
            
            # Crear resumen por fecha y evento
            logs_summary = df_logs.groupby(['fecha', 'evento']).agg({
                'total': 'sum',
                'numero_factura': 'count',
                'vendedor': lambda x: list(set(x)),
                'periodo_dia': lambda x: x.value_counts().to_dict()
            }).reset_index()
            
            logs_summary.columns = ['fecha', 'evento', 'total_monto', 'num_eventos', 'vendedores', 'distribucion_periodo']
            
            # Convertir a formato para MongoDB
            logs_records = logs_summary.to_dict('records')
            
            # Procesar fechas para MongoDB
            for record in logs_records:
                record['fecha'] = pd.to_datetime(record['fecha'])
                record['fecha_procesamiento'] = pd.Timestamp.now()
            
            # Conectar a MongoDB y guardar
            db = self.db_config.get_mongo_database()
            collection = db['resumen_logs_diario']
            
            # Eliminar registros existentes para las fechas
            fechas_a_cargar = [record['fecha'] for record in logs_records]
            collection.delete_many({'fecha': {'$in': fechas_a_cargar}})
            
            # Insertar nuevos registros
            if logs_records:
                collection.insert_many(logs_records)
                logger.info(f"Cargados {len(logs_records)} registros de resumen de logs")
            
        except Exception as e:
            logger.error(f"Error cargando resumen de logs: {str(e)}")
            raise
    
    def generate_data_quality_report(self, transformed_data):
        """
        Generar reporte de calidad de datos
        
        Args:
            transformed_data (dict): Datos transformados
        
        Returns:
            dict: Reporte de calidad
        """
        try:
            logger.info("Generando reporte de calidad de datos")
            
            quality_report = {
                'fecha_reporte': pd.Timestamp.now(),
                'resumen_datasets': {}
            }
            
            for dataset_name, df in transformed_data.items():
                if not df.empty:
                    quality_report['resumen_datasets'][dataset_name] = {
                        'total_registros': len(df),
                        'columnas': len(df.columns),
                        'valores_nulos': df.isnull().sum().sum(),
                        'duplicados': df.duplicated().sum(),
                        'memoria_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
                    }
            
            # Guardar reporte en MongoDB
            db = self.db_config.get_mongo_database()
            collection = db['reportes_calidad']
            collection.insert_one(quality_report)
            
            logger.info("Reporte de calidad generado y guardado")
            return quality_report
            
        except Exception as e:
            logger.error(f"Error generando reporte de calidad: {str(e)}")
            raise
    
    def load_all_data(self, transformed_data):
        """
        Cargar todos los datos transformados
        
        Args:
            transformed_data (dict): Diccionario con datos transformados
        """
        try:
            logger.info("Iniciando carga completa de datos")
            
            # Cargar resumen diario si existe
            if 'resumen_diario' in transformed_data:
                self.load_daily_summary(transformed_data['resumen_diario'])
            
            # Cargar análisis de inventario si existe
            if 'analisis_inventario' in transformed_data:
                self.load_inventory_analysis(transformed_data['analisis_inventario'])
            
            # Cargar resumen de logs si existe
            if 'logs_processed' in transformed_data:
                self.load_logs_summary(transformed_data['logs_processed'])
            
            # Generar reporte de calidad
            self.generate_data_quality_report(transformed_data)
            
            logger.info("Carga completa de datos finalizada")
            
        except Exception as e:
            logger.error(f"Error en carga completa: {str(e)}")
            raise

# Función helper para Airflow
def load_data_task(**context):
    """Task function para Airflow"""
    loader = DataLoader()
    fecha_ejecucion = context['ds']
    
    # Cargar datos transformados
    transformed_data = {}
    data_types = ['resumen_diario', 'analisis_inventario', 'logs_processed']
    
    for data_type in data_types:
        try:
            file_path = f'/opt/airflow/data/processed/{data_type}_{fecha_ejecucion}.csv'
            transformed_data[data_type] = pd.read_csv(file_path)
            logger.info(f"Cargados datos transformados de {data_type}: {len(transformed_data[data_type])} registros")
        except FileNotFoundError:
            logger.warning(f"No se encontró archivo transformado para {data_type}")
            transformed_data[data_type] = pd.DataFrame()
    
    # Cargar todos los datos
    loader.load_all_data(transformed_data)
    
    return "Carga completada"
