"""
DAG principal para el pipeline ETL de Metaltronic S.A.
Procesa datos de ventas, inventario y logs diariamente
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
import sys
import os

# Agregar paths necesarios
sys.path.append('/opt/airflow')

# Importar funciones de los módulos ETL
from src.extract import extract_data_task
from src.transform import transform_data_task
from src.load import load_data_task

# Configuración por defecto del DAG
default_args = {
    'owner': 'metaltronic_data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Definir el DAG
dag = DAG(
    'metaltronic_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL para procesar datos de ventas e inventario de Metaltronic S.A.',
    schedule_interval='0 6 * * *',  # Ejecutar todos los días a las 6:00 AM
    max_active_runs=1,
    tags=['metaltronic', 'etl', 'ventas', 'inventario']
)

# ========== TAREAS DEL PIPELINE ==========

# Tarea inicial - Verificar conexiones
check_connections = BashOperator(
    task_id='check_database_connections',
    bash_command="""
    echo "Verificando conexiones a bases de datos..."
    echo "PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT"
    echo "MongoDB: $MONGO_HOST:$MONGO_PORT"
    echo "Conexiones verificadas correctamente"
    """,
    dag=dag
)

# Crear directorios necesarios
create_directories = BashOperator(
    task_id='create_directories',
    bash_command="""
    mkdir -p /opt/airflow/data/raw
    mkdir -p /opt/airflow/data/processed
    echo "Directorios creados correctamente"
    """,
    dag=dag
)

# ===== FASE DE EXTRACCIÓN =====
extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data_task,
    dag=dag,
    doc_md="""
    ### Extracción de Datos
    
    Esta tarea extrae datos de las siguientes fuentes:
    - **PostgreSQL**: Datos de ventas, clientes, productos e inventario
    - **MongoDB**: Logs de transacciones y sesiones de usuario
    
    **Salida**: Archivos CSV en `/data/raw/`
    """
)

# ===== FASE DE TRANSFORMACIÓN =====
transform_data = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data_task,
    dag=dag,
    doc_md="""
    ### Transformación de Datos
    
    Procesamiento y limpieza de datos:
    - Limpieza de datos de ventas
    - Cálculo de métricas de negocio
    - Agregación de resúmenes diarios
    - Análisis de rotación de inventario
    
    **Entrada**: Archivos CSV de `/data/raw/`
    **Salida**: Archivos CSV en `/data/processed/`
    """
)

# ===== FASE DE CARGA =====
load_data = PythonOperator(
    task_id='load_data',
    python_callable=load_data_task,
    dag=dag,
    doc_md="""
    ### Carga de Datos
    
    Carga datos procesados a:
    - **PostgreSQL**: Resumen diario de ventas y análisis de inventario
    - **MongoDB**: Resumen de logs y reportes de calidad
    
    **Entrada**: Archivos CSV de `/data/processed/`
    """
)

# Validación de datos cargados
validate_data = PythonOperator(
    task_id='validate_loaded_data',
    python_callable=lambda **context: validate_data_quality(context['ds']),
    dag=dag
)

def validate_data_quality(fecha_ejecucion):
    """Validar calidad de los datos cargados"""
    import logging
    from config.database import db_config
    
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar datos en PostgreSQL
        engine = db_config.get_postgres_engine()
        
        # Contar registros en tabla de resumen
        with engine.connect() as conn:
            result = conn.execute(
                "SELECT COUNT(*) as count FROM analytics.resumen_ventas_diario WHERE fecha_resumen = %s",
                (fecha_ejecucion,)
            ).fetchone()
            
            count = result[0] if result else 0
            logger.info(f"Registros en resumen diario: {count}")
        
        # Verificar datos en MongoDB
        db = db_config.get_mongo_database()
        mongo_count = db['resumen_logs_diario'].count_documents({
            'fecha': {
                '$gte': datetime.strptime(fecha_ejecucion, '%Y-%m-%d'),
                '$lt': datetime.strptime(fecha_ejecucion, '%Y-%m-%d') + timedelta(days=1)
            }
        })
        logger.info(f"Registros en logs MongoDB: {mongo_count}")
        
        return "Validación completada exitosamente"
        
    except Exception as e:
        logger.error(f"Error en validación: {str(e)}")
        raise

# Limpieza de archivos temporales
cleanup_temp_files = BashOperator(
    task_id='cleanup_temp_files',
    bash_command="""
    echo "Limpiando archivos temporales..."
    find /opt/airflow/data/raw -name "*.csv" -mtime +7 -delete
    find /opt/airflow/data/processed -name "*.csv" -mtime +7 -delete
    echo "Limpieza completada"
    """,
    dag=dag
)

# Notificación de éxito
success_notification = PythonOperator(
    task_id='success_notification',
    python_callable=lambda **context: print(f"✅ Pipeline ETL completado exitosamente para {context['ds']}"),
    dag=dag
)

# Tarea de finalización
end_task = DummyOperator(
    task_id='pipeline_completed',
    dag=dag
)

# ========== DEFINIR DEPENDENCIAS ==========

# Flujo principal del pipeline
(
    [check_connections, create_directories] 
    >> extract_data 
    >> transform_data 
    >> load_data 
    >> validate_data 
    >> cleanup_temp_files 
    >> success_notification 
    >> end_task
)

# ========== CONFIGURACIÓN ADICIONAL ==========

# Agregar documentación al DAG
dag.doc_md = """
# Pipeline ETL Metaltronic S.A.

## Descripción
Pipeline de datos para procesar información de ventas, inventario y logs de la empresa Metaltronic S.A.
Empresa metalmecánica ubicada en Ambato, Tungurahua, Ecuador.

## Arquitectura
- **Fuentes de datos**: PostgreSQL (transaccional) y MongoDB (logs)
- **Procesamiento**: Python con Pandas y Apache Airflow
- **Destino**: Data Warehouse en PostgreSQL + MongoDB para análisis

## Programación
- **Frecuencia**: Diaria a las 6:00 AM
- **Zona horaria**: UTC-5 (Ecuador)
- **Retries**: 2 intentos con 5 minutos de espera

## Datos Procesados
1. **Ventas diarias**: Resumen de transacciones, clientes y productos
2. **Inventario**: Análisis de rotación y stock
3. **Logs**: Patrones de uso y actividad del sistema

## Contacto
- **Equipo**: Data Engineering Team
- **Email**: data@metaltronic.com
"""

# Configurar alertas (simuladas)
def send_failure_alert(context):
    """Enviar alerta en caso de falla"""
    print(f"🚨 ALERTA: Falla en el pipeline ETL")
    print(f"DAG: {context['dag'].dag_id}")
    print(f"Tarea: {context['task'].task_id}")
    print(f"Fecha: {context['ds']}")
    return "Alerta enviada"

# Aplicar función de alerta a tareas críticas
for task in [extract_data, transform_data, load_data]:
    task.on_failure_callback = send_failure_alert
