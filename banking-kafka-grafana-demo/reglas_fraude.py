"""
reglas_fraude.py — Única fuente de verdad para las reglas de fraude.

Importado tanto por consumer_b (que detecta y publica alertas) como por
consumer_c (que expone métricas), para que ambos evalúen exactamente
el mismo criterio y nunca se desincronicen.
"""

from schema import EventoTransaccion

UMBRAL_COMPRA_RETIRO = 2_000_000
UMBRAL_GENERAL       = 5_000_000


def evaluar_fraude(evento: EventoTransaccion) -> str | None:
    """Retorna el motivo de la alerta, o None si la transacción es normal."""
    if evento.monto > UMBRAL_GENERAL:
        return f"Monto extremadamente alto: ${evento.monto:,.0f} COP"

    if evento.tipo in ("compra", "retiro") and evento.monto > UMBRAL_COMPRA_RETIRO:
        return (
            f"{evento.tipo.capitalize()} inusual: "
            f"${evento.monto:,.0f} COP supera umbral de ${UMBRAL_COMPRA_RETIRO:,}"
        )

    return None