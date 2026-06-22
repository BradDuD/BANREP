"""
producer_stress.py — Generador de carga para Kafka

Objetivo:
- Máximo throughput posible.
- Sin tablas Rich.
- Sin logs por evento.
- Sin esperas (sleep).
- Envío asíncrono.
- Estadísticas de TPS cada segundo.
"""

import json
import time
import sys
import os

from kafka import KafkaProducer

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from schema import generar_transaccion


# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

KAFKA_BROKER = "localhost:9092"
TOPIC = "transacciones"

BATCH_SIZE = 1000


# ─── PRODUCER ────────────────────────────────────────────────────────────────

def crear_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,

        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),

        # Optimizaciones de throughput
        linger_ms=10,
        batch_size=65536,
        compression_type="gzip",
        acks=1,
    )


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BANREP Kafka Stress Producer")
    print(f"Broker : {KAFKA_BROKER}")
    print(f"Topic  : {TOPIC}")
    print("=" * 70)

    producer = crear_producer()

    total = 0
    ultimo_total = 0
    inicio = time.time()

    try:
        while True:

            # Envío masivo
            for _ in range(BATCH_SIZE):

                evento = generar_transaccion()

                producer.send(
                    TOPIC,
                    key=evento.cc,
                    value=evento.model_dump(),
                )

                total += 1

            producer.flush()

            ahora = time.time()

            if ahora - inicio >= 1:

                tps = total - ultimo_total

                print(
                    f"TPS: {tps:>8,} | "
                    f"Total enviados: {total:>12,}"
                )

                ultimo_total = total
                inicio = ahora

    except KeyboardInterrupt:

        print("\nDeteniendo producer...")

        producer.flush()
        producer.close()

        print(f"Total enviados: {total:,}")


if __name__ == "__main__":
    main()