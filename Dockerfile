FROM apache/airflow:2.7.0-python3.9

USER root

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copiar requirements y instalar dependencias Python
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Inicializar la base de datos de Airflow
RUN airflow db init

# Crear usuario admin
RUN airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Metaltronic \
    --role Admin \
    --email admin@metaltronic.com \
    --password admin123
