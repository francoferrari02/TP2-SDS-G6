#!/usr/bin/env python3
"""Comparación de tiempos del Cell Index Method: TP1 (Python) vs TP2 (C++).

Etapa 8 del TP2 (`plan_desarrollo_tp2/08_rendimiento_cim.md`). Mide
EXCLUSIVAMENTE la operación de búsqueda de vecinos (reconstrucción de celdas
+ comparación de candidatos), sin generación de partículas, I/O, animación ni
ninguna otra parte de ninguno de los dos motores. La generación de
partículas se hace una única vez por punto, fuera del bucle cronometrado
(misma convención que ya usa `benchmark.py` del TP1).

Se corren TRES condiciones, no dos, para poder separar la causa de la
diferencia en vez de solo constatarla:

  A) TP1 tal como está construido: partículas con radio no nulo
     (r ~ U[0.23,0.26], generadas sin superposición por rejection sampling),
     criterio de vecindad borde-borde. Es el TP1 real.
  B) TP1 con una ablación a partículas puntuales (r=0 para todas): mismo
     código de TP1 (`buscar_vecinos_cim`), pero sin la restricción de no
     superposición (con r=0 la condición de rechazo nunca se activa) y con
     el mismo criterio geométrico que usa TP2 (distancia centro-centro).
     Aísla el efecto de "tener radio" del efecto de "estar escrito en
     Python vs. C++".
  C) TP2: `cell_index_neighbors` (C++), partículas puntuales, periódico.

Las tres usan el mismo `N`, `L=20`, `rc=1`, condición de borde periódica, y
cada una con su propio `M` óptimo (`calcular_M_max` de cada implementación):
esto no se fuerza a ser igual a propósito, porque la diferencia de `M_max`
entre A (radio no nulo) y B/C (puntuales) es en sí misma una de las causas
que se quiere mostrar (menor M -> celdas más grandes -> más partículas por
celda -> más comparaciones).

Entorno de esta corrida (registrar en el informe, ver etapa 8):
  - TP1: Python 3.13.9, numpy/pandas del venv de cell-index-method.
  - TP2: C++17, compilado con `clang++ -std=c++17 -O2` (Apple clang 17.0.0),
    sin flags de profiling ni sanitizers.
  - Ambos en la misma máquina (macOS, arm64), en la misma sesión, sin otras
    cargas de cómputo intencionales corriendo en paralelo.

Uso:
    python3 python/benchmark_tp1_vs_tp2.py
"""

import csv
import subprocess
import sys
import time
from pathlib import Path

TP2_ROOT = Path(__file__).resolve().parent.parent
TP1_ROOT = Path("/Users/katiamenshikoff/Documents/ITBA/SDS/cell-index-method")
TP1_PYTHON = TP1_ROOT / "venv" / "bin" / "python"
TP2_BENCHMARK_BIN = TP2_ROOT / "build" / "benchmark_cim"

L = 20.0
RC = 1.0
N_GRID = [10, 25, 50, 100, 200, 400, 800]
REPETICIONES = 100
SEED = 12345

# Radios de TP1 (default de su enunciado): r ~ U[0.23, 0.26].
R_MIN, R_MAX = 0.23, 0.26


def run_tp1(condicion_puntual: bool):
    """Corre la condición A (radio real) o B (ablación puntual) de TP1.

    Se ejecuta como subproceso separado por punto de N para que el tiempo
    de warm-up del intérprete/import de numpy no contamine ninguna medición
    (cada subproceso paga ese costo una vez, fuera de la zona cronometrada,
    igual que se excluye el arranque del proceso en TP2).
    """
    r_min, r_max = (0.0, 0.0) if condicion_puntual else (R_MIN, R_MAX)

    def build_script(n: int) -> str:
        return f"""
import sys, time, json
sys.path.insert(0, {str(TP1_ROOT)!r})
import numpy as np
from src.particles import generar_particulas
from src.cim import buscar_vecinos_cim, calcular_M_max

L = {L}
RC = {RC}
N = {n}
REPS = {REPETICIONES}
SEED = {SEED}
r_min, r_max = {r_min}, {r_max}

resultado = generar_particulas(N, lado=L, r_min=r_min, r_max=r_max, seed=SEED,
                                periodic=True, max_intentos=2_000_000)
posiciones = resultado["posiciones"]
radios = resultado["radios"]
m = calcular_M_max(L, RC, float(radios.max()) if N > 0 else 0.0)

tiempos = np.empty(REPS, dtype=float)
total_vecinos = 0
for k in range(REPS):
    t0 = time.perf_counter()
    vecinos = buscar_vecinos_cim(posiciones, radios, L, m, RC, periodic=True)
    tiempos[k] = time.perf_counter() - t0
    if k == REPS - 1:
        total_vecinos = sum(len(v) for v in vecinos.values())

mean_k = (total_vecinos / N) if N > 0 else 0.0
print(json.dumps({{
    "N": N, "M": m, "mean": float(np.mean(tiempos)), "std": float(np.std(tiempos)),
    "mean_k": mean_k,
}}))
"""

    rows = []
    for n in N_GRID:
        proc = subprocess.run(
            [str(TP1_PYTHON), "-c", build_script(n)],
            capture_output=True, text=True, cwd=str(TP1_ROOT),
        )
        if proc.returncode != 0:
            print(f"  FALLO TP1 (puntual={condicion_puntual}) N={n}:\n{proc.stderr}", file=sys.stderr)
            continue
        import json
        row = json.loads(proc.stdout.strip().splitlines()[-1])
        rows.append(row)
        print(f"  TP1 (puntual={condicion_puntual}) N={row['N']:>5} M={row['M']:>3} "
              f"mean={row['mean']*1000:.4f}ms std={row['std']*1000:.4f}ms mean_k={row['mean_k']:.3f}")
    return rows


def run_tp2():
    if not TP2_BENCHMARK_BIN.exists():
        print(f"No se encontro {TP2_BENCHMARK_BIN}. Compilar primero.", file=sys.stderr)
        sys.exit(1)
    rows = []
    for n in N_GRID:
        proc = subprocess.run(
            [str(TP2_BENCHMARK_BIN), str(L), str(RC), str(n), str(REPETICIONES), str(SEED)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print(f"  FALLO TP2 N={n}:\n{proc.stderr}", file=sys.stderr)
            continue
        line = proc.stdout.strip()
        n_out, mean, std = line.split(",")
        # mean_k del stderr: "# N=.. vecinos_totales_ultima_corrida=.. mean_k=.."
        mean_k = float(proc.stderr.strip().split("mean_k=")[-1])
        row = {"N": int(n_out), "M": 20, "mean": float(mean), "std": float(std), "mean_k": mean_k}
        rows.append(row)
        print(f"  TP2            N={row['N']:>5} M={row['M']:>3} "
              f"mean={row['mean']*1000:.4f}ms std={row['std']*1000:.4f}ms mean_k={row['mean_k']:.3f}")
    return rows


def main():
    print(f"Parametros comunes: L={L}, rc={RC}, periodic=True, N={N_GRID}, "
          f"repeticiones={REPETICIONES}, seed={SEED}\n")

    print("Condicion A: TP1 real (radio U[0.23,0.26], no superposicion)")
    rows_a = run_tp1(condicion_puntual=False)

    print("\nCondicion B: TP1 ablacion puntual (r=0, sin restriccion de superposicion)")
    rows_b = run_tp1(condicion_puntual=True)

    print("\nCondicion C: TP2 (C++, cell_index_neighbors, puntual)")
    rows_c = run_tp2()

    summary_dir = TP2_ROOT / "data" / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    out_path = summary_dir / "benchmark_tp1_vs_tp2.csv"
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["condicion", "N", "M", "tiempo_promedio_s", "tiempo_std_s", "mean_k"])
        for label, rows in [("tp1_radio", rows_a), ("tp1_puntual", rows_b), ("tp2", rows_c)]:
            for row in rows:
                writer.writerow([label, row["N"], row["M"], row["mean"], row["std"], row["mean_k"]])

    print(f"\nEscrito: {out_path.relative_to(TP2_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
