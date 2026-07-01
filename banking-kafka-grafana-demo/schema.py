"""
schema.py — Modelo del evento de transacción
Compartido entre producer y consumers.
"""

import uuid
import random
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# ─── MODELO DEL EVENTO ────────────────────────────────────────────────────────

class EventoTransaccion(BaseModel):
    evento_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cc: str
    nombre: str
    tipo: str                    # transferencia | pago | compra | retiro
    monto: float
    moneda: str = "COP"
    comercio: str | None = None
    region: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ─── DATOS MOCK / SIMULACIÓN ──────────────────────────────────────────────────────

CLIENTES = [
    {"cc": "12.345.678-9", "nombre": "Valentina Rojas Fuentes"},
    {"cc": "15.678.901-2", "nombre": "Matías Contreras Pizarro"},
    {"cc": "11.222.333-4", "nombre": "Camila Soto Herrera"},
    {"cc": "16.987.654-3", "nombre": "Diego Muñoz Araya"},
    {"cc": "13.456.789-0", "nombre": "Javiera Espinoza Lagos"},
    {"cc": "14.321.654-K", "nombre": "Sebastián Vidal Morales"},
    {"cc": "17.654.321-5", "nombre": "Constanza Medina Riquelme"},
    {"cc": "10.987.654-6", "nombre": "Nicolás Fuentes Bravo"},
]

TIPOS_TRANSACCION = ["transferencia", "pago", "compra", "retiro"]

COMERCIOS = [
    "Falabella", "D1", "Tiendas ARA", "Dollarcity", "Rappi",
    "Claro", "Movistar", "Netflix", "Uber","OXXO"
    "Didi", "Copec", "Farmacia Cruz Verde",
    "McDonald's", "KFC", "Koaj",
    None, None,  # transferencias no tienen comercio
]

REGIONES = [
    "Usaquén", "Chapinero", "Santa Fe",
    "San Cristóbal", "Usme", "Tunjuelito",
    "Bosa", "Kennedy", "Fontibón",
    "Engativá", "Suba",
    "Barrios Unidos", "Teusaquillo", "Los Mártires",
    "Antonio Nariño", "Puente Aranda", "La Candelaria",
    "Rafael Uribe Uribe", "Ciudad Bolívar", "Sumapaz",
]

# Rangos de monto por tipo (en COP)
RANGOS_MONTO = {
    "transferencia": (50_000, 5_000_000),
    "pago":          (2_000, 1_000_000),
    "compra":        (1_000, 3_000_000),
    "retiro":        (10_000, 800_000),
}


def generar_transaccion() -> EventoTransaccion:
    """Genera una transacción aleatoria con datos al aleatorios."""
    cliente = random.choice(CLIENTES)
    tipo = random.choice(TIPOS_TRANSACCION)
    monto_min, monto_max = RANGOS_MONTO[tipo]

    # Simula ocasionalmente montos sospechosos (fraude)
    if random.random() < 0.08:  # 8% de probabilidad
        monto = random.uniform(8_000_000, 20_500_000)
    else:
        monto = random.uniform(monto_min, monto_max)

    return EventoTransaccion(
        cc=cliente["cc"],
        nombre=cliente["nombre"],
        tipo=tipo,
        monto=round(monto, 2),
        comercio=random.choice(COMERCIOS) if tipo != "transferencia" else None,
        region=random.choice(REGIONES),
    )
