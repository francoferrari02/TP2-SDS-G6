#!/usr/bin/env python3
"""Refinamiento de la grilla de eta entre 0 y 1.5 (paso 0.2), para todas las
densidades del estudio del votante (rho=2,4,8 y las densidades bajas de
clusters rho=1/pi,1/(2pi),1/(3pi)).

Motivo: la caída de <va> es más rápida justamente en esa zona (ver
plan_desarrollo_tp2/05_pilotos_y_grilla_eta.md); agregar puntos ahí resuelve
mejor la curva sin cambiar el modelo, la matriz de estudio ni el protocolo
ya acordado (R=20, steps=3000).

Escribe las corridas nuevas DENTRO de los mismos directorios de piloto ya
existentes (data/pilots/voter_eta_study_1/ y
data/pilots/voter_lowrho_cluster_study_1/), usando indices de eta nuevos
(11..16) que no colisionan con los ya usados (0..10) en el esquema de
semillas, para no pisar ninguna corrida anterior. Después de correr esto,
volver a ejecutar voter_eta_study_analyze.py / voter_lowrho_cluster_study_*
sobre esos mismos run-name para que las tablas resumen incluyan los puntos
nuevos junto a los viejos.

Uso:
    python3 python/voter_eta_refine_run.py [--steps N] [--realizations N]
        [--jobs N] [--dry-run]
"""

import argparse
import csv
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIMULATE_BIN = REPO_ROOT / "build" / "simulate"

# Puntos nuevos entre eta=0 y eta=1.5, paso 0.2 (0 y 1.5 ya existen en la
# grilla original y no se repiten aca).
NEW_ETA_POINTS = [0.2, 0.4, 0.6, 0.8, 1.2, 1.4]
# Continua la indexacion de la grilla original (0..10) sin superponerse.
NEW_ETA_INDEX_START = 11

MODEL = "voter"

# (rho_nominal, N, rho_label, seed_offset, run_name) -- run_name es el
# directorio de piloto ya existente donde hay que agregar estas corridas.
DENSITY_SETS = [
    (2.0, 200, "rho_2", 0, "voter_eta_study_1"),
    (4.0, 400, "rho_4", 30000, "voter_eta_study_1"),
    (8.0, 800, "rho_8", 60000, "voter_eta_study_1"),
    (1.0 / 3.141592653589793, 32, "rho_1_over_pi", 0, "voter_lowrho_cluster_study_1"),
    (1.0 / (2.0 * 3.141592653589793), 16, "rho_1_over_2pi", 20000, "voter_lowrho_cluster_study_1"),
    (1.0 / (3.0 * 3.141592653589793), 11, "rho_1_over_3pi", 40000, "voter_lowrho_cluster_study_1"),
]

SEED_BASE = {
    "voter_eta_study_1": 900000,
    "voter_lowrho_cluster_study_1": 950000,
}


def seed_for(run_name: str, seed_offset: int, eta_index: int, realization: int) -> int:
    return SEED_BASE[run_name] + seed_offset + 100 * eta_index + realization


def build_command(output_dir: Path, rho_nominal: float, rho_label: str, n: int,
                   eta: float, steps: int, seed: int, realization: int) -> list:
    return [
        str(SIMULATE_BIN),
        "--model", MODEL,
        "--rho-nominal", repr(rho_nominal),
        "--rho-label", rho_label,
        "--N", str(n),
        "--eta", repr(eta),
        "--steps", str(steps),
        "--base-seed", str(seed),
        "--realization", str(realization),
        "--output-dir", str(output_dir),
        "--observables-stride", "1",
        "--overwrite",
    ]


def run_one(cmd):
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    return result, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--realizations", type=int, default=20)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SIMULATE_BIN.exists() and not args.dry_run:
        print(f"No se encontro el binario {SIMULATE_BIN}. Compilar primero.", file=sys.stderr)
        return 1

    realizations = list(range(args.realizations))

    combos = []
    for rho_nominal, n, rho_label, seed_offset, run_name in DENSITY_SETS:
        output_dir = REPO_ROOT / "data" / "pilots" / run_name
        for local_index, eta in enumerate(NEW_ETA_POINTS):
            eta_index = NEW_ETA_INDEX_START + local_index
            for realization in realizations:
                seed = seed_for(run_name, seed_offset, eta_index, realization)
                combos.append((output_dir, rho_nominal, rho_label, n, eta, seed, realization))

    print(f"Total de corridas nuevas: {len(combos)} "
          f"({len(DENSITY_SETS)} densidades x {len(NEW_ETA_POINTS)} etas nuevos x "
          f"{len(realizations)} realizaciones), steps={args.steps}")

    if args.dry_run:
        for output_dir, rho_nominal, rho_label, n, eta, seed, realization in combos:
            cmd = build_command(output_dir, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
            print(" ".join(cmd))
        return 0

    jobs = []
    for output_dir, rho_nominal, rho_label, n, eta, seed, realization in combos:
        cmd = build_command(output_dir, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
        jobs.append((cmd, rho_label, eta, seed, realization))

    n_fail = 0
    total_start = time.time()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_one, job[0]): job for job in jobs}
        completed = 0
        for future, job in futures.items():
            result, elapsed = future.result()
            cmd, rho_label, eta, seed, realization = job
            completed += 1
            ok = result.returncode == 0
            if not ok:
                n_fail += 1
                print(f"[{completed}/{len(jobs)}] FALLO {rho_label} eta={eta} rea={realization} "
                      f"seed={seed} (rc={result.returncode})")
                print(result.stdout, file=sys.stdout)
                print(result.stderr, file=sys.stderr)
            elif completed % 50 == 0 or completed == len(jobs):
                print(f"[{completed}/{len(jobs)}] OK (ultima: {rho_label} eta={eta} rea={realization}, {elapsed:.2f}s)")

    total_elapsed = time.time() - total_start
    print(f"\nTiempo total: {total_elapsed:.1f}s, fallos: {n_fail}/{len(jobs)}")

    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
