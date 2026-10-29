import random
import time
from datetime import datetime, timezone, timedelta
import psycopg2
from psycopg2.extras import execute_values

# Conexión por defecto a TimescaleDB
DB_CONFIG = {
    "dbname": "timescaledb",
    "user": "timescale_user",
    "password": "timescale_password",
    "host": "localhost",
    "port": 5433
}

TOTAL_RECORDS = 50_000
BATCH_SIZE = 5_000

# Subsistemas y módulos 
SUBSYSTEMS = [
    ("EPS", ["battery_voltage", "solar_current", "battery_temp"], "V"),
    ("COMMS", ["rssi", "snr", "pa_temp"], "dBm"),
    ("ADCS", ["gyro_x", "gyro_y", "gyro_z"], "deg/s"),
    ("THERMAL", ["temp_panel_top", "temp_obc"], "degC"),
    ("PAYLOAD", ["sensor_optical_val", "radiation_dose"], "rad")
]

def generate_telemetry_batch(batch_size: int, current_timestamp: datetime):
    batch = []
    t = current_timestamp

    for _ in range(batch_size):
        t += timedelta(milliseconds=100)
        subsystem, modules, unit = random.choice(SUBSYSTEMS)
        module = random.choice(modules)
        val = round(random.uniform(0.5, 120.0), 3)
        raw_hex = f"5445494445{random.randint(1000, 9999):X}{int(t.timestamp()):X}"

        batch.append((
            'TM',                  # message_type
            'SATELLITE',           # source
            'GROUND',              # destination
            t,                     # timestamp
            subsystem,             # subsystem
            module,                # module
            raw_hex,               # raw_data
            val,                   # value
            unit,                  # unit
            True                   # valid
        ))

    return batch, t

def run_benchmark():
    print("=== INICIANDO BENCHMARK EN DEV (control_telemetrymessage) ===")
    print(f"Destino   : {DB_CONFIG['host']}:{DB_CONFIG['port']} ({DB_CONFIG['dbname']})")
    print(f"Objetivo  : {TOTAL_RECORDS:,} filas | Batch size: {BATCH_SIZE:,}\n")

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO control_telemetrymessage (
            message_type,
            source,
            destination,
            timestamp,
            subsystem,
            module,
            raw_data,
            value,
            unit,
            valid
        ) VALUES %s;
    """

    start_time = time.perf_counter()
    current_time = datetime.now(timezone.utc) - timedelta(days=5)
    records_inserted = 0

    try:
        while records_inserted < TOTAL_RECORDS:
            batch, current_time = generate_telemetry_batch(BATCH_SIZE, current_time)

            t0 = time.perf_counter()
            execute_values(cursor, insert_query, batch, page_size=BATCH_SIZE)
            conn.commit()
            t1 = time.perf_counter()

            records_inserted += len(batch)
            print(f"[{records_inserted:6,}/{TOTAL_RECORDS:,}] Batch insertado en {t1 - t0:.3f} s")

    except Exception as e:
        conn.rollback()
        print(f"\n[!] Error durante la inserción: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    total_time = time.perf_counter() - start_time
    rate = records_inserted / total_time

    print("\n=== RESULTADOS ===")
    print(f"Filas insertadas : {records_inserted:,}")
    print(f"Tiempo total     : {total_time:.2f} s")
    print(f"Rendimiento      : {rate:,.2f} inserts/segundo")

if __name__ == "__main__":
    run_benchmark()