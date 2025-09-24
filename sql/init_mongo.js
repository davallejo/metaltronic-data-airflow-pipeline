// Script de inicialización para MongoDB
// Base de datos: metaltronic_mongo

// Conectar a la base de datos
db = db.getSiblingDB('metaltronic_mongo');

// Crear colección de logs de ventas
db.createCollection('logs_ventas');

// Insertar datos de ejemplo para logs de ventas
db.logs_ventas.insertMany([
    {
        "timestamp": new Date("2024-01-15T08:30:00Z"),
        "evento": "venta_completada",
        "numero_factura": "001-001-000001",
        "cliente_id": 1,
        "vendedor": "Ana García",
        "total": 504.00,
        "productos": [
            {"codigo": "MT-001", "cantidad": 20},
            {"codigo": "MT-005", "cantidad": 400}
        ],
        "metadatos": {
            "ip_cliente": "192.168.1.10",
            "sucursal": "Ambato",
            "terminal": "POS-001"
        }
    },
    {
        "timestamp": new Date("2024-01-16T10:15:00Z"),
        "evento": "venta_completada",
        "numero_factura": "001-001-000002",
        "cliente_id": 2,
        "vendedor": "Carlos López",
        "total": 1400.90,
        "productos": [
            {"codigo": "MT-002", "cantidad": 15},
            {"codigo": "MT-004", "cantidad": 65}
        ],
        "metadatos": {
            "ip_cliente": "192.168.1.11",
            "sucursal": "Ambato",
            "terminal": "POS-002"
        }
    },
    {
        "timestamp": new Date("2024-01-17T14:20:00Z"),
        "evento": "venta_completada",
        "numero_factura": "001-001-000003",
        "cliente_id": 3,
        "vendedor": "Ana García",
        "total": 358.96,
        "productos": [
            {"codigo": "MT-006", "cantidad": 80},
            {"codigo": "MT-007", "cantidad": 120}
        ],
        "metadatos": {
            "ip_cliente": "192.168.1.12",
            "sucursal": "Ambato",
            "terminal": "POS-001"
        }
    }
]);

// Crear colección de sesiones de usuario
db.createCollection('sesiones_usuario');

// Insertar datos de sesiones
db.sesiones_usuario.insertMany([
    {
        "usuario_id": "ana.garcia",
        "nombre_completo": "Ana García",
        "fecha_inicio": new Date("2024-01-15T07:30:00Z"),
        "fecha_fin": new Date("2024-01-15T16:30:00Z"),
        "terminal": "POS-001",
        "ventas_realizadas": 3,
        "total_vendido": 1071.83
    },
    {
        "usuario_id": "carlos.lopez",
        "nombre_completo": "Carlos López",
        "fecha_inicio": new Date("2024-01-16T08:00:00Z"),
        "fecha_fin": new Date("2024-01-16T17:00:00Z"),
        "terminal": "POS-002",
        "ventas_realizadas": 4,
        "total_vendido": 4579.96
    }
]);

// Crear índices para optimizar consultas
db.logs_ventas.createIndex({"timestamp": 1});
db.logs_ventas.createIndex({"evento": 1});
db.logs_ventas.createIndex({"numero_factura": 1});
db.sesiones_usuario.createIndex({"usuario_id": 1});
db.sesiones_usuario.createIndex({"fecha_inicio": 1});

print("Inicialización de MongoDB completada para Metaltronic S.A.");
