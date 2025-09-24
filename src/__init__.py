"""
Módulo principal del pipeline ETL de Metaltronic S.A.
Pipeline de datos para procesar ventas, inventario y logs
"""

__version__ = "1.0.0"
__author__ = "Metaltronic Data Engineering Team"
__description__ = "Pipeline ETL para datos de empresa metalmecánica"

from .extract import DataExtractor
from .transform import DataTransformer  
from .load import DataLoader

__all__ = ['DataExtractor', 'DataTransformer', 'DataLoader']
