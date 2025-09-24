-- Script de inicialización para PostgreSQL
-- Base de datos: Metaltronic S.A.

-- Crear esquemas
CREATE SCHEMA IF NOT EXISTS ventas;
CREATE SCHEMA IF NOT EXISTS inventario;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Tabla de productos metalmecánicos
CREATE TABLE inventario.productos (
    id_producto SERIAL PRIMARY KEY,
    codigo_producto VARCHAR(20) UNIQUE NOT NULL,
    nombre_producto VARCHAR(200) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    material VARCHAR(50) NOT NULL,
    peso_kg DECIMAL(10,3),
    precio_unitario DECIMAL(10,2) NOT NULL,
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 10,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de clientes
CREATE TABLE ventas.clientes (
    id_cliente SERIAL PRIMARY KEY,
    cedula_ruc VARCHAR(20) UNIQUE NOT NULL,
    nombre_cliente VARCHAR(200) NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100),
    ciudad VARCHAR(50),
    provincia VARCHAR(50) DEFAULT 'Tungurahua',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de ventas (transacciones)
CREATE TABLE ventas.transacciones (
    id_transaccion SERIAL PRIMARY KEY,
    numero_factura VARCHAR(20) UNIQUE NOT NULL,
    id_cliente INTEGER REFERENCES ventas.clientes(id_cliente),
    fecha_venta DATE NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    iva DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    metodo_pago VARCHAR(30) NOT NULL,
    vendedor VARCHAR(100) NOT NULL,
    sucursal VARCHAR(50) DEFAULT 'Ambato',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de detalle de ventas
CREATE TABLE ventas.detalle_ventas (
    id_detalle SERIAL PRIMARY KEY,
    id_transaccion INTEGER REFERENCES ventas.transacciones(id_transaccion),
    id_producto INTEGER REFERENCES inventario.productos(id_producto),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(5,2) DEFAULT 0,
    subtotal DECIMAL(12,2) NOT NULL
);

-- Tabla de resumen para analytics (destino ETL)
CREATE TABLE analytics.resumen_ventas_diario (
    fecha_resumen DATE PRIMARY KEY,
    total_ventas DECIMAL(15,2),
    total_transacciones INTEGER,
    productos_vendidos INTEGER,
    cliente_mas_frecuente VARCHAR(200),
    categoria_mas_vendida VARCHAR(50),
    promedio_ticket DECIMAL(10,2),
    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de ejemplo

-- Productos metalmecánicos
INSERT INTO inventario.productos (codigo_producto, nombre_producto, categoria, material, peso_kg, precio_unitario, stock_actual, stock_minimo) VALUES
('MT-001', 'Tubo Cuadrado 40x40x2mm', 'Tuberia', 'Acero Negro', 2.35, 15.50, 150, 20),
('MT-002', 'Plancha Lisa 3mm', 'Lamina', 'Acero Negro', 23.55, 45.80, 80, 10),
('MT-003', 'Varilla Corrugada 12mm', 'Varilla', 'Acero Corrugado', 0.888, 1.25, 500, 50),
('MT-004', 'Angulo 50x50x5mm', 'Perfil', 'Acero Negro', 3.77, 8.90, 200, 25),
('MT-005', 'Electrodo 6011 3.2mm', 'Soldadura', 'Rutilico', 0.02, 0.35, 1000, 100),
('MT-006', 'Disco Corte Metal 7"', 'Herramienta', 'Abrasivo', 0.15, 2.75, 300, 30),
('MT-007', 'Perno Hexagonal M12x50', 'Tornilleria', 'Acero Galvanizado', 0.08, 0.85, 800, 100),
('MT-008', 'Tubo Redondo 2" SCH40', 'Tuberia', 'Acero Negro', 5.44, 25.60, 120, 15),
('MT-009', 'Chapa Antideslizante 4mm', 'Lamina', 'Acero Negro', 31.4, 67.20, 50, 8),
('MT-010', 'Cable Soldadura 2/0', 'Soldadura', 'Cobre', 0.75, 12.30, 250, 25);

-- Clientes
INSERT INTO ventas.clientes (cedula_ruc, nombre_cliente, telefono, email, ciudad, provincia) VALUES
('1804123456001', 'Constructora Andina Cía. Ltda.', '032850123', 'ventas@constructoraandina.com', 'Ambato', 'Tungurahua'),
('1805987654001', 'Metalmecánica Tungurahua S.A.', '032741258', 'compras@metaltungurahua.com', 'Ambato', 'Tungurahua'),
('1803456789001', 'Talleres Unidos Cía. Ltda.', '032963147', 'administracion@talleresunidos.com', 'Ambato', 'Tungurahua'),
('1801654321001', 'Industrias Metálicas del Centro', '032852963', 'gerencia@metalcentro.ec', 'Ambato', 'Tungurahua'),
('0502741258001', 'Construcciones Chimborazo S.A.', '032159753', 'proyectos@conschimborazo.com', 'Riobamba', 'Chimborazo'),
('1804567890123', 'Juan Carlos Pérez (Persona Natural)', '0987654321', 'jcperez@gmail.com', 'Ambato', 'Tungurahua'),
('1805432167890', 'María Elena Sánchez', '0998765432', 'mesanchez@hotmail.com', 'Ambato', 'Tungurahua'),
('1803789456123', 'Carlos Enrique Vásquez', '0976543210', 'carlosvasquez@yahoo.com', 'Pelileo', 'Tungurahua');

-- Transacciones de venta
INSERT INTO ventas.transacciones (numero_factura, id_cliente, fecha_venta, subtotal, iva, total, metodo_pago, vendedor, sucursal) VALUES
('001-001-000001', 1, '2024-01-15', 450.00, 54.00, 504.00, 'Transferencia', 'Ana García', 'Ambato'),
('001-001-000002', 2, '2024-01-16', 1250.80, 150.10, 1400.90, 'Cheque', 'Carlos López', 'Ambato'),
('001-001-000003', 3, '2024-01-17', 320.50, 38.46, 358.96, 'Efectivo', 'Ana García', 'Ambato'),
('001-001-000004', 1, '2024-01-18', 780.25, 93.63, 873.88, 'Crédito', 'María Rodríguez', 'Ambato'),
('001-001-000005', 4, '2024-01-19', 2150.40, 258.05, 2408.45, 'Transferencia', 'Carlos López', 'Ambato'),
('001-001-000006', 5, '2024-01-20', 890.75, 106.89, 997.64, 'Cheque', 'Ana García', 'Ambato'),
('001-001-000007', 6, '2024-01-21', 185.60, 22.27, 207.87, 'Efectivo', 'María Rodríguez', 'Ambato'),
('001-001-000008', 7, '2024-01-22', 95.40, 11.45, 106.85, 'Efectivo', 'Ana García', 'Ambato'),
('001-001-000009', 2, '2024-01-23', 1580.90, 189.71, 1770.61, 'Transferencia', 'Carlos López', 'Ambato'),
('001-001-000010', 8, '2024-01-24', 420.30, 50.44, 470.74, 'Crédito', 'María Rodríguez', 'Ambato');

-- Detalle de ventas
INSERT INTO ventas.detalle_ventas (id_transaccion, id_producto, cantidad, precio_unitario, descuento, subtotal) VALUES
-- Factura 1
(1, 1, 20, 15.50, 0, 310.00),
(1, 5, 400, 0.35, 0, 140.00),
-- Factura 2
(2, 2, 15, 45.80, 2.00, 672.60),
(2, 4, 65, 8.90, 0, 578.50),
-- Factura 3
(3, 6, 80, 2.75, 0, 220.00),
(3, 7, 120, 0.85, 0.50, 100.50),
-- Factura 4
(4, 3, 450, 1.25, 0, 562.50),
(4, 10, 18, 12.30, 1.50, 217.75),
-- Factura 5
(5, 8, 45, 25.60, 0, 1152.00),
(5, 9, 15, 67.20, 1.00, 998.40),
-- Factura 6
(6, 1, 35, 15.50, 0, 542.50),
(6, 4, 40, 8.90, 0.50, 348.25),
-- Factura 7
(7, 5, 250, 0.35, 0, 87.50),
(7, 6, 36, 2.75, 0, 99.00),
-- Factura 8
(8, 7, 95, 0.85, 0, 80.75),
(8, 10, 1, 12.30, 0, 12.30),
-- Factura 9
(9, 2, 22, 45.80, 0, 1007.60),
(9, 3, 350, 1.25, 0, 437.50),
-- Factura 10
(10, 4, 48, 8.90, 0, 427.20);

-- Crear índices para optimizar consultas
CREATE INDEX idx_productos_categoria ON inventario.productos(categoria);
CREATE INDEX idx_productos_activo ON inventario.productos(activo);
CREATE INDEX idx_transacciones_fecha ON ventas.transacciones(fecha_venta);
CREATE INDEX idx_transacciones_cliente ON ventas.transacciones(id_cliente);
CREATE INDEX idx_detalle_transaccion ON ventas.detalle_ventas(id_transaccion);
CREATE INDEX idx_detalle_producto ON ventas.detalle_ventas(id_producto);
