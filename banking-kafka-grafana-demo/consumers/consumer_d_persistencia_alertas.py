"""
consumer_d_persistencia_alertas.py — Consumer Group: persistencia-alertas
Topic: alertas → PostgreSQL (tabla alertas_fraude)

Consumer D Persistencia Alertas (PostgreSQL)
Consumer independiente del que detecta el fraude (consumer_b).
Su única responsabilidad es persistir las alertas para histórico/auditoría,
complementando las métricas en vivo de Prometheus con un registro durable.
"""

import json
import time
import sys
import os

import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer
from rich.console import Console
from rich.panel import Panel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

KAFKA_BROKER = "localhost:9092"
TOPIC = "alertas"
GROUP_ID = "persistencia-alertas"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "transacciones_db",
    "user": "banrep",
    "password": "banrep123",
}

BATCH_SIZE = 20          # salvavidas si llega una ráfaga de alertas
FLUSH_INTERVAL = 0.5     # las alertas se persisten casi en tiempo real
POLL_TIMEOUT_MS = 200

console = Console()


# ─── PERSISTENCIA EN LOTE ─────────────────────────────────────────────────────

def insertar_lote(conn, alertas: list[dict]) -> None:
    if not alertas:
        return

    valores = [
        (
            a["evento_id"], a["cc"], a["nombre"], a["tipo"],
            a["monto"], a["region"], a["motivo"], a["timestamp"],
        )
        for a in alertas
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO alertas_fraude
                (evento_id, cc, nombre, tipo, monto, region, motivo, timestamp)
            VALUES %s
            ON CONFLICT (evento_id) DO NOTHING
            """,
            valores,
            page_size=len(valores),
        )

    conn.commit()


# ─── CONSUMER ─────────────────────────────────────────────────────────────────

def main():
    console.print(Panel(
        f"[bold yellow]Consumer D — Persistencia de Alertas PostgreSQL[/]\n"
        f"Group: [cyan]{GROUP_ID}[/] | Topic: [cyan]{TOPIC}[/]\n\n"
        "[dim]Guarda en alertas_fraude el histórico de fraude detectado.\n"
        "Independiente de consumer_b y de consumer_alertas.[/]",
        title="🗄️  BANREP Consumer D",
        border_style="yellow",
    ))

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    conn = psycopg2.connect(**DB_CONFIG)
    console.print("[green]✓ Conectado a PostgreSQL[/]\n")

    buffer: list[dict] = []
    total_guardadas = 0
    last_flush = time.time()

    def flush():
        nonlocal buffer, total_guardadas, last_flush
        if not buffer:
            return
        insertar_lote(conn, buffer)
        consumer.commit()
        total_guardadas += len(buffer)
        console.print(f"[yellow]🗄️  {total_guardadas:,} alertas persistidas (lote de {len(buffer)})[/]")
        buffer = []
        last_flush = time.time()

    try:
        while True:
            registros = consumer.poll(timeout_ms=POLL_TIMEOUT_MS)

            for _, mensajes in registros.items():
                for mensaje in mensajes:
                    buffer.append(mensaje.value)

            ahora = time.time()
            if len(buffer) >= BATCH_SIZE or (buffer and ahora - last_flush >= FLUSH_INTERVAL):
                flush()

    except KeyboardInterrupt:
        console.print("\n[yellow]Consumer D detenido. Vaciando buffer restante...[/]")
        flush()
    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()