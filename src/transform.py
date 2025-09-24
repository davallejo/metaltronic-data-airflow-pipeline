"""
Módulo de Transformación de Datos
Metaltronic S.A. - Pipeline ETL
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    """Clase para transformar y limpiar datos"""
    
    def __init__(self):
        pass
    
    def clean_sales_data(self, df_ventas):
        """
        Limpiar y transformar datos de ventas
        
        Args:
            df_ventas (pd.DataFrame): DataFrame de ventas sin procesar
        
        Returns:
            pd.DataFrame: DataFrame de ventas limpio
        """
        try:
            logger.info("Iniciando limpieza de datos de ventas")
            
            if df_ventas.empty:
                logger.warning("DataFrame de ventas está vacío")
                return df_ventas
            
            # Crear copia para evitar modificar original
            df = df_ventas.copy()
            
            # Limpiar datos nulos
            df = df.dropna(subset=['numero_factura', 'fecha_venta'])
            
            # Convertir tipos de datos
            df['fecha_venta'] = pd.to_datetime(df['fecha_venta'])
            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
            df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce')
            df['descuento'] = pd.to_numeric(df['descuento'], errors='coerce').fillna(0)
            df['subtotal'] = pd.to_numeric(df['subtotal'], errors='coerce')
            
            # Calcular métricas adicionales
            df['precio_con_descuento'] = df['precio_unitario'] * (1 - df['descuento']/100)
            df['margen_descuento'] = df['precio_unitario'] - df['precio_con_descuento']
            df['valor_total_producto'] = df['cantidad'] * df['precio_con_descuento']
            
            # Categorizar métodos de pago
            df['tipo_pago'] = df['metodo_pago'].map({
                'Efectivo': 'Inmediato',
                'Transferencia': 'Inmediato',
                'Cheque': 'Diferido',
                'Crédito': 'Diferido'
            }).fillna('Otro')
            
            # Crear categorías de ventas por monto
            df['categoria_venta'] = pd.cut(df['total_factura'], 
                                         bins=[0, 200, 500, 1000, float('inf')],
                                         labels=['Pequeña', 'Mediana', 'Grande', 'Muy Grande'])
            
            # Agregar información temporal
            df['año'] = df['fecha_venta'].dt.year
            df['mes'] = df['fecha_venta'].dt.month
            df['dia_semana'] = df['fecha_venta'].dt.day_name()
            df['trimestre'] = df['fecha_venta'].dt.quarter
            
            logger.info(f"Datos de ventas limpiados: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Error limpiando datos de ventas: {str(e)}")
            raise
    
    def aggregate_daily_sales(self, df_ventas):
        """
        Crear resumen diario de ventas
        
        Args:
            df_ventas (pd.DataFrame): DataFrame de ventas limpio
        
        Returns:
            pd.DataFrame: Resumen diario de ventas
        """
        try:
            logger.info("Creando resumen diario de ventas")
            
            if df_ventas.empty:
                logger.warning("DataFrame de ventas está vacío")
                return pd.DataFrame()
            
            # Agrupar por fecha
            daily_summary = df_ventas.groupby('fecha_venta').agg({
                'total_factura': ['sum', 'mean', 'count'],
                'cantidad': 'sum',
                'nombre_cliente': 'nunique',
                'categoria': lambda x: x.value_counts().index[0] if not x.empty else None,
                'vendedor': lambda x: x.value_counts().index[0] if not x.empty else None
            }).reset_index()
            
            # Aplanar columnas
            daily_summary.columns = [
                'fecha_resumen', 'total_ventas', 'promedio_ticket', 
                'total_transacciones', 'productos_vendidos', 
                'clientes_unicos', 'categoria_mas_vendida', 'vendedor_top'
            ]
            
            # Calcular cliente más frecuente por día
            clientes_frecuentes = df_ventas.groupby(['fecha_venta', 'nombre_cliente']).size().reset_index(name='frecuencia')
            clientes_top = clientes_frecuentes.loc[clientes_frecuentes.groupby('fecha_venta')['frecuencia'].idxmax()]
            
            # Merge con resumen diario
            daily_summary = daily_summary.merge(
                clientes_top[['fecha_venta', 'nombre_cliente']].rename(columns={'nombre_cliente': 'cliente_mas_frecuente'}),
                left_on='fecha_resumen',
                right_on='fecha_venta',
                how='left'
            ).drop('fecha_venta', axis=1)
            
            # Agregar timestamp de procesamiento
            daily_summary['fecha_procesamiento'] = datetime.now()
            
            logger.info(f"Resumen diario creado: {len(daily_summary)} días")
            return daily_summary
            
        except Exception as e:
            logger.error(f"Error creando resumen diario: {str(e)}")
            raise
    
    def analyze_inventory_trends(self, df_inventario, df_ventas):
        """
        Analizar tendencias de inventario vs ventas
        
        Args:
            df_inventario (pd.DataFrame): DataFrame de inventario
            df_ventas (pd.DataFrame): DataFrame de ventas
        
        Returns:
            pd.DataFrame: Análisis de inventario
        """
        try:
            logger.info("Analizando tendencias de inventario")
            
            if df_inventario.empty or df_ventas.empty:
                logger.warning("DataFrames de inventario o ventas están vacíos")
                return pd.DataFrame()
            
            # Calcular ventas por producto
            ventas_producto = df_ventas.groupby('codigo_producto').agg({
                'cantidad': 'sum',
                'subtotal': 'sum',
                'id_transaccion': 'nunique'
            }).reset_index()
            
            ventas_producto.columns = ['codigo_producto', 'cantidad_vendida', 'ingresos_producto', 'num_transacciones']
            
            # Merge con inventario
            inventory_analysis = df_inventario.merge(ventas_producto, on='codigo_producto', how='left')
            
            # Rellenar valores nulos (productos sin ventas)
            inventory_analysis['cantidad_vendida'] = inventory_analysis['cantidad_vendida'].fillna(0)
            inventory_analysis['ingresos_producto'] = inventory_analysis['ingresos_producto'].fillna(0)
            inventory_analysis['num_transacciones'] = inventory_analysis['num_transacciones'].fillna(0)
            
            # Calcular métricas
            inventory_analysis['rotacion_inventario'] = (
                inventory_analysis['cantidad_vendida'] / inventory_analysis['stock_actual']
            ).replace([np.inf, -np.inf], 0).fillna(0)
            
            inventory_analysis['dias_stock'] = (
                inventory_analysis['stock_actual'] / inventory_analysis['cantidad_vendida'] * 30
            ).replace([np.inf, -np.inf], 999).fillna(999)
            
            # Clasificar productos por performance
            inventory_analysis['performance'] = pd.cut(
                inventory_analysis['rotacion_inventario'],
                bins=[-np.inf, 0.1, 0.5, 1.0, np.inf],
                labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
            )
            
            logger.info(f"Análisis de inventario completado: {len(inventory_analysis)} productos")
            return inventory_analysis
            
        except Exception as e:
            logger.error(f"Error analizando inventario: {str(e)}")
            raise
    
    def process_logs_data(self, df_logs):
        """
        Procesar datos de logs de MongoDB
        
        Args:
            df_logs (pd.DataFrame): DataFrame de logs
        
        Returns:
            pd.DataFrame: Logs procesados
        """
        try:
            logger.info("Procesando datos de logs")
            
            if df_logs.empty:
                logger.warning("DataFrame de logs está vacío")
                return df_logs
            
            # Crear copia
            df = df_logs.copy()
            
            # Convertir timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['fecha'] = df['timestamp'].dt.date
            df['hora'] = df['timestamp'].dt.hour
            
            # Extraer información de productos si existe
            if 'productos' in df.columns:
                df['num_productos'] = df['productos'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            
            # Categorizar por hora del día
            df['periodo_dia'] = pd.cut(df['hora'], 
                                     bins=[-1, 6, 12, 18, 24],
                                     labels=['Madrugada', 'Mañana', 'Tarde', 'Noche'])
            
            logger.info(f"Logs procesados: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Error procesando logs: {str(e)}")
            raise
    
    def transform_all_data(self, raw_data):
        """
        Transformar todos los datos del pipeline
        
        Args:
            raw_data (dict): Diccionario con datos sin procesar
        
        Returns:
            dict: Diccionario con datos transformados
        """
        try:
            logger.info("Iniciando transformación completa de datos")
            
            transformed_data = {}
            
            # Transformar datos de ventas
            if 'ventas' in raw_data and not raw_data['ventas'].empty:
                transformed_data['ventas_clean'] = self.clean_sales_data(raw_data['ventas'])
                transformed_data['resumen_diario'] = self.aggregate_daily_sales(transformed_data['ventas_clean'])
                
                # Análisis de inventario si hay datos
                if 'inventario' in raw_data and not raw_data['inventario'].empty:
                    transformed_data['analisis_inventario'] = self.analyze_inventory_trends(
                        raw_data['inventario'], 
                        transformed_data['ventas_clean']
                    )
            
            # Procesar logs
            if 'logs' in raw_data and not raw_data['logs'].empty:
                transformed_data['logs_processed'] = self.process_logs_data(raw_data['logs'])
            
            logger.info("Transformación completa finalizada")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error en transformación completa: {str(e)}")
            raise

# Función helper para Airflow
def transform_data_task(**context):
    """Task function para Airflow"""
    transformer = DataTransformer()
    fecha_ejecucion = context['ds']
    
    # Cargar datos sin procesar
    raw_data = {}
    data_types = ['ventas', 'inventario', 'logs']
    
    for data_type in data_types:
        try:
            file_path = f'/opt/airflow/data/raw/{data_type}_{fecha_ejecucion}.csv'
            raw_data[data_type] = pd.read_csv(file_path)
            logger.info(f"Cargados datos de {data_type}: {len(raw_data[data_type])} registros")
        except FileNotFoundError:
            logger.warning(f"No se encontró archivo para {data_type}")
            raw_data[data_type] = pd.DataFrame()
    
    # Transformar datos
    transformed_data = transformer.transform_all_data(raw_data)
    
    # Guardar datos transformados
    import os
    os.makedirs('/opt/airflow/data/processed', exist_ok=True)
    
    for key, df in transformed_data.items():
        if not df.empty:
            file_path = f'/opt/airflow/data/processed/{key}_{fecha_ejecucion}.csv'
            df.to_csv(file_path, index=False)
            logger.info(f"Datos transformados de {key} guardados en {file_path}")
    
    return "Transformación completada"
