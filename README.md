# 🏭 Pipeline ETL Metaltronic S.A.

**Pipeline de datos para empresa metalmecánica ecuatoriana**

[![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

## 📋 Descripción del Proyecto

Sistema ETL (Extract, Transform, Load) desarrollado para **Metaltronic S.A.**, empresa metalmecánica ubicada en Ecuador. El pipeline procesa diariamente datos de ventas, inventario y logs operacionales para generar insights de negocio.

### 🎯 Objetivo
Automatizar el procesamiento de datos transaccionales y generar reportes analíticos que permitan:
- Monitorear el desempeño de ventas diarias
- Optimizar la gestión de inventario
- Analizar patrones de comportamiento del sistema

## 🏗️ Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Fuentes de Datos"
        A[PostgreSQL<br/>Ventas & Inventario]
        B[MongoDB<br/>Logs del Sistema]
    end
    
    subgraph "Pipeline ETL - Apache Airflow"
        C[Extract<br/>Extracción]
        D[Transform<br/>Transformación]
        E[Load<br/>Carga]
    end
    
    subgraph "Destinos Analíticos"
        F[PostgreSQL<br/>Data Warehouse]
        G[MongoDB<br/>Reportes de Calidad]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
```

## 🛠️ Stack Tecnológico

### Lenguajes y Frameworks
- **Python 3.9+**: Lenguaje principal para ETL
- **SQL**: Consultas y modelado de datos
- **Pandas**: Manipulación y análisis de datos
- **SQLAlchemy**: ORM para bases de datos relacionales

### Bases de Datos
- **PostgreSQL 13**: Base de datos transaccional y data warehouse
- **MongoDB 5.0**: Almacenamiento de logs y documentos no estructurados

### Herramientas ETL y Orquestación
- **Apache Airflow 2.7**: Orquestación del pipeline
- **Docker & Docker Compose**: Containerización y despliegue

### Plataformas Cloud (Simuladas Localmente)
- **Almacenamiento**: Simulación de AWS S3 con volúmenes Docker
- **Procesamiento**: Contenedores que simulan servicios cloud

## 📁 Estructura del Proyecto

```
metaltronic-data-pipeline/
├── 📄 README.md                    # Documentación principal
├── 📄 docker-compose.yml           # Configuración de contenedores
├── 📄 Dockerfile                   # Imagen personalizada Airflow
├── 📄 requirements.txt             # Dependencias Python
├── 📄 .env                        # Variables de entorno
├── 📄 .gitignore                  # Archivos ignorados por Git
├── 📂 sql/
│   ├── 📄 init_postgres.sql       # Datos iniciales PostgreSQL
│   └── 📄 init_mongo.js           # Datos iniciales MongoDB
├── 📂 dags/
│   └── 📄 metaltronic_etl_dag.py  # DAG principal de Airflow
├── 📂 src/
│   ├── 📄 __init__.py
│   ├── 📄 extract.py              # Módulo de extracción
│   ├── 📄 transform.py            # Módulo de transformación
│   └── 📄 load.py                 # Módulo de carga
├── 📂 config/
│   └── 📄 database.py             # Configuración de conexiones
└── 📂 data/
    ├── 📂 raw/                    # Datos sin procesar
    └── 📂 processed/              # Datos transformados
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker Desktop 4.0+ instalado
- Git para clonar el repositorio
- 8GB RAM disponible (recomendado)
- Puertos disponibles: 5432, 27017, 8080, 6379

### 1. Clonar el Repositorio
```bash
git clone https://github.com/davallejo/metaltronic-data-airflow-pipeline.git
cd metaltronic-data-pipeline
```

### 2. Configurar Variables de Entorno
```bash
# El archivo .env ya está incluido con valores por defecto
# Opcional: personalizar credenciales si es necesario
cp .env .env.local
```

### 3. Construir y Ejecutar los Contenedores
```bash
# Construir las imágenes
docker-compose build

# Ejecutar en segundo plano
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```
<img width="1346" height="183" alt="image" src="https://github.com/user-attachments/assets/453db7c1-bd65-48a4-bf3c-ce98b208a356" />


### 4. Verificar la Instalación
```bash
# Verificar logs de Airflow
docker-compose logs airflow-webserver

# Verificar conexión a PostgreSQL
docker-compose exec postgres psql -U metaltronic_user -d metaltronic_db -c "\dt ventas.*"

# Verificar conexión a MongoDB
docker-compose exec mongodb mongo -u mongo_user -p mongo_pass --authenticationDatabase admin
```
<img width="1360" height="245" alt="image" src="https://github.com/user-attachments/assets/951db8f5-9296-47ac-bfb5-a7d7e81d98ad" />

<img width="1360" height="182" alt="image" src="https://github.com/user-attachments/assets/00004c22-b564-4a15-a7d2-4b97e160d7fc" />

<img width="1360" height="158" alt="image" src="https://github.com/user-attachments/assets/41e3c634-9f39-4c5d-9f04-4aa142238b5d" />


## 🎮 Uso del Sistema

### Acceso a la Interfaz Web de Airflow
1. Abrir navegador en: http://localhost:8081
2. **Usuario**: `admin`
3. **Contraseña**: `admin123`

<img width="1437" height="416" alt="image" src="https://github.com/user-attachments/assets/9d743c29-d120-4f9d-8dc7-9eae721588dc" />


### Ejecutar el Pipeline ETL

#### Ejecución Manual
1. En la interfaz de Airflow, buscar el DAG: `metaltronic_etl_pipeline`
2. Activar el DAG con el toggle
3. Hacer clic en "Trigger DAG" para ejecutar manualmente

<img width="1450" height="468" alt="image" src="https://github.com/user-attachments/assets/8c142522-24d1-4466-af62-08a96ef13733" />


#### Ejecución Programada
- El pipeline se ejecuta automáticamente todos los días a las 6:00 AM
- Procesa los datos del día anterior

### Monitorear la Ejecución
```bash
# Ver logs del pipeline
docker-compose logs -f airflow-scheduler

# Ver logs específicos
docker-compose exec airflow-webserver airflow dags list-runs -d metaltronic_etl_pipeline
```
<img width="1175" height="265" alt="image" src="https://github.com/user-attachments/assets/95277ff4-f413-45e0-a07b-d195c7523947" />

<img width="1371" height="161" alt="image" src="https://github.com/user-attachments/assets/391fe451-10b8-4418-af10-87907ee8fe7b" />



## 🧪 Pruebas y Validación

### 1. Verificar Datos de Origen
```sql
-- Conectar a PostgreSQL
docker-compose exec postgres psql -U metaltronic_user -d metaltronic_db

-- Verificar datos de ventas
SELECT * FROM ventas.transacciones;
SELECT * FROM ventas.detalle_ventas;
SELECT * FROM inventario.productos;
```
<img width="1643" height="265" alt="image" src="https://github.com/user-attachments/assets/817b42d2-f4ea-4b07-a9e2-5b64ddb74fd3" />

<img width="959" height="289" alt="image" src="https://github.com/user-attachments/assets/dbcb5231-c218-4a55-a228-3e5e5fdc088b" />

<img width="1748" height="316" alt="image" src="https://github.com/user-attachments/assets/5989cd1a-48c1-4af0-acc7-4dbda8781cef" />


```javascript
// Conectar a MongoDB
docker-compose exec mongodb mongo -u mongo_user -p mongo_pass --authenticationDatabase admin

use metaltronic_mongo
db.logs_ventas.find().limit(5).pretty()
db.sesiones_usuario.count()
```
<img width="1135" height="139" alt="image" src="https://github.com/user-attachments/assets/0ba293b0-7818-4af3-b1fb-7f4ab34f500b" />

<img width="691" height="599" alt="image" src="https://github.com/user-attachments/assets/407d8b06-ee97-4e32-a66d-7d82ea63271e" />

<img width="725" height="92" alt="image" src="https://github.com/user-attachments/assets/32a97132-6363-4e2f-9bf4-4a0d31a4f829" />

### 2. Ejecutar Pipeline Completo
```bash
# Ejecutar DAG específico para una fecha
docker-compose exec airflow-webserver airflow dags trigger metaltronic_etl_pipeline

# Monitorear estado
docker-compose exec airflow-webserver \
  airflow dags list-runs -d metaltronic_etl_pipeline --no-backfill | grep success

# Ver los estados de las tasks de un DAG Run usando run_id
docker-compose exec airflow-webserver \
  airflow tasks states-for-dag-run metaltronic_etl_pipeline scheduled__2024-01-04T06:00:00+00:00
```
<img width="882" height="291" alt="image" src="https://github.com/user-attachments/assets/bc925ae6-903f-4065-af26-407d0c5ea66a" />

<img width="1135" height="485" alt="image" src="https://github.com/user-attachments/assets/78898937-5ed6-41c9-b912-0ba6815990fe" />

<img width="1386" height="389" alt="image" src="https://github.com/user-attachments/assets/5dacb0fb-81a1-4429-883d-31083f4a401c" />


### 3. Validar Resultados
```sql
-- Verificar datos procesados en PostgreSQL
SELECT * FROM analytics.resumen_ventas_diario ORDER BY fecha_resumen DESC LIMIT 5;
SELECT * FROM analytics.analisis_inventario WHERE performance = 'Alto' LIMIT 10;
```

### 4. Casos de Prueba
- ✅ **Extracción**: Verificar que se extraigan datos de ambas fuentes
- ✅ **Transformación**: Validar cálculos de métricas de negocio
- ✅ **Carga**: Confirmar inserción en tablas de destino
- ✅ **Calidad**: Revisar reportes de calidad de datos

## 📊 Datos y Métricas Generadas

### Resumen Diario de Ventas
- Total de ventas por día
- Número de transacciones
- Productos más vendidos
- Clientes más frecuentes
- Promedio de ticket de compra

### Análisis de Inventario
- Rotación de inventario por producto
- Días de stock disponible
- Productos con bajo stock
- Performance de ventas por categoría

### Reportes de Calidad
- Completitud de datos
- Valores duplicados
- Métricas de procesamiento
- Logs de errores y advertencias

## 🔧 Comandos Útiles

### Gestión de Contenedores
```bash
# Detener todos los servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart airflow-webserver

# Ver logs en tiempo real
docker-compose logs -f [nombre-servicio]

# Limpiar volúmenes (CUIDADO: borra todos los datos)
docker-compose down -v
```

### Gestión de Airflow
```bash
# Reiniciar el scheduler
docker-compose exec airflow-scheduler airflow scheduler

# Listar DAGs
docker-compose exec airflow-webserver airflow dags list

# Pausar/despausar un DAG
docker-compose exec airflow-webserver airflow dags pause metaltronic_etl_pipeline
docker-compose exec airflow-webserver airflow dags unpause metaltronic_etl_pipeline
```

### Acceso a Bases de Datos
```bash
# PostgreSQL
docker-compose exec postgres psql -U metaltronic_user -d metaltronic_db

# MongoDB
docker-compose exec mongodb mongo -u mongo_user -p mongo_pass --authenticationDatabase admin
```

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error: Puerto ya en uso
```bash
# Verificar puertos ocupados
netstat -tulpn | grep :8080
# Cambiar puerto en docker-compose.yml o liberar puerto
```

#### Error: Falta de memoria
```bash
# Verificar uso de memoria
docker stats
# Incrementar memoria de Docker Desktop
```

#### Error: Conexión a base de datos
```bash
# Verificar estado de contenedores
docker-compose ps
# Revisar logs de la base de datos
docker-compose logs postgres
docker-compose logs mongodb
```

### Logs de Depuración
```bash
# Logs detallados de Airflow
docker-compose exec airflow-webserver airflow config list
docker-compose logs airflow-webserver | grep ERROR

# Logs de pipeline
tail -f data/processed/*.log
```

## 🚦 Monitoreo y Alertas

### Métricas Clave
- ⏱️ **Tiempo de ejecución**: < 15 minutos por pipeline completo
- 📊 **Tasa de éxito**: > 95% de ejecuciones exitosas
- 💾 **Volumen de datos**: ~1000-5000 registros diarios
- 🔄 **Frecuencia**: Ejecución diaria automática

### Alertas Configuradas
- ❌ Falla en extracción de datos
- ⚠️ Datos faltantes o inconsistentes
- 🕐 Pipeline tardando más de 30 minutos
- 💾 Espacio en disco bajo (< 2GB disponible)

## 👥 Contribución y Desarrollo

### Configuración de Desarrollo
```bash
# Clonar y configurar entorno de desarrollo
git clone [repo-url]
cd metaltronic-data-pipeline

# Crear rama de desarrollo
git checkout -b feature/nueva-funcionalidad

# Instalar dependencias locales (opcional)
pip install -r requirements.txt
```

### Convenciones de Código
- **Python**: Seguir PEP 8
- **SQL**: Usar UPPERCASE para palabras clave
- **Git**: Commits descriptivos en español
- **Documentación**: Comentarios en español

### Testing
```bash
# Ejecutar tests unitarios (cuando estén disponibles)
pytest tests/

# Validar sintaxis SQL
docker-compose exec postgres psql -U metaltronic_user -d metaltronic_db -f sql/test_queries.sql
```

### Equipo de Desarrollo
- **Diego Vallejo**

### Licencia
Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

**⚡ ¡Pipeline listo para procesar datos metalmecánicos ecuatorianos!**

*Desarrollado con ❤️ por el equipo de Ingeniería de Datos*
