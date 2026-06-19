-- Tabla principal de transacciones
CREATE TABLE IF NOT EXISTS transacciones (
    id          SERIAL PRIMARY KEY,
    evento_id   VARCHAR(36)    NOT NULL UNIQUE,
    cc         VARCHAR(12)    NOT NULL,
    nombre      VARCHAR(100)   NOT NULL,
    tipo        VARCHAR(30)    NOT NULL,
    monto       NUMERIC(14, 2) NOT NULL,
    moneda      VARCHAR(5)     DEFAULT 'COP',
    comercio    VARCHAR(100),
    region      VARCHAR(50),
    timestamp   TIMESTAMPTZ    NOT NULL,
    creado_en   TIMESTAMPTZ    DEFAULT NOW()
);

-- Tabla de alertas de fraude
CREATE TABLE IF NOT EXISTS alertas_fraude (
    id          SERIAL PRIMARY KEY,
    evento_id   VARCHAR(36)    NOT NULL,
    cc         VARCHAR(12)    NOT NULL,
    monto       NUMERIC(14, 2) NOT NULL,
    motivo      VARCHAR(200)   NOT NULL,
    timestamp   TIMESTAMPTZ    NOT NULL,
    creado_en   TIMESTAMPTZ    DEFAULT NOW()
);

-- Índice para consultas por cc
CREATE INDEX IF NOT EXISTS idx_transacciones_cc ON transacciones(cc);
CREATE INDEX IF NOT EXISTS idx_alertas_cc ON alertas_fraude(cc);
