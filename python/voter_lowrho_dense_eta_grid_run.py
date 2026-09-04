#!/usr/bin/env python3
"""Lanzador de los puntos nuevos de la grilla densa de eta para el votante, densidades bajas.

Analogo a vicsek_lowrho_dense_eta_grid_run.py: corre los mismos 23 puntos
nuevos de eta (paso 0.2 entre eta=0.6 y eta=6.2) para las tres densidades
bajas de clusters (rho=1/pi,1/(2pi),1/(3pi), N=32,16,11), esta vez para el
votante, para que su figura combinada de <S> vs. eta (seis densidades) tenga
la misma resolucion que la de Vicsek.

Mismo protocolo que el resto del barrido final: steps=3000, R=20, CIM, sin
trayectoria. Semillas deterministas `2200000 + rho_offset + 100*eta_index +
realizacion`, sin colision con ningun lote previo (el maximo de semilla
reservado hasta ahora era 2100000 + 60000 + 100*22 + 19 = 2162219, en
vicsek_lowrho_dense_eta_grid_run.py).

Uso:
    python3 python/voter_lowrho_dense_eta_grid_run.py [--run-name NOMBRE]
        [--steps N] [--realizations N] [--jobs N] [--dry-run]
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

NEW_ETA_GRID = [
    0.60, 0.80,
    1.20, 1.40, 1.60, 1.80,
    2.20, 2.40, 2.60, 2.80,
    3.20, 3.40, 3.60, 3.80,
    4.20, 4.40, 4.60, 4.80,
    5.20, 5.40, 5.60, 5.80,
    6.20,
]

RHO_GRID = [
    (1.0 / 3.14159265358979323846, 32, "rho_1_over_pi"),
    (1.0 / (2.0 * 3.14159265358979323846), 16, "rho_1_over_2pi"),
    (1.0 / (3.0 * 3.14159265358979323846), 11, "rho_1_over_3pi"),
]

SEED_BASE = 2200000
RHO_SEED_OFFSET = {"rho_1_over_pi": 0, "rho_1_over_2pi": 30000, "rho_1_over_3pi": 60000}


def seed_for(rho_label: str, eta_index: int, realization: int) -> int:
    return SEED_BASE + RHO_SEED_OFFSET[rho_label] + 100 * eta_index + realization


def build_command(output_dir: Path, rho_nominal: float, rho_label: str,
                   n: int, eta: float, steps: int, seed: int, realization: int) -> list:
    return [
        str(SIMULATE_BIN),
        "--model", "voter",
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


def build_combos(realizations):
    combos = []
    for rho_nominal, n, rho_label in RHO_GRID:
        for eta_index, eta in enumerate(NEW_ETA_GRID):
            for realization in realizations:
                seed = seed_for(rho_label, eta_index, realization)
                combos.append((rho_nominal, rho_label, n, eta, eta_index, seed, realization))
    return combos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="voter_lowrho_dense_eta_grid_steps3000_R20_v1")
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--realizations", type=int, default=20)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SIMULATE_BIN.exists() and not args.dry_run:
        print(f"No se encontro el binario {SIMULATE_BIN}. Compilar primero.", file=sys.stderr)
        return 1

    output_dir = REPO_ROOT / "data" / "pilots" / args.run_name
    summary_dir = REPO_ROOT / "data" / "summary"
    manifest_path = summary_dir / f"{args.run_name}_manifest.csv"
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)

    realizations = list(range(args.realizations))
    combos = build_combos(realizations)

    print(f"Total de corridas: {len(combos)} "
          f"({len(RHO_GRID)} densidades bajas x {len(NEW_ETA_GRID)} etas x "
          f"{len(realizations)} realizaciones), steps={args.steps}, output_dir={output_dir}")

    if args.dry_run:
        for rho_nominal, rho_label, n, eta, eta_index, seed, realization in combos:
            cmd = build_command(output_dir, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
            print(" ".join(cmd))
        return 0

    jobs = []
    for rho_nominal, rho_label, n, eta, eta_index, seed, realization in combos:
        cmd = build_command(output_dir, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
        jobs.append((cmd, rho_nominal, rho_label, n, eta, eta_index, seed, realization))

    rows = []
    n_fail = 0
    total_start = time.time()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_one, job[0]): job for job in jobs}
        completed = 0
        for future, job in futures.items():
            result, elapsed = future.result()
            cmd, rho_nominal, rho_label, n, eta, eta_index, seed, realization = job
            completed += 1
            ok = result.returncode == 0
            if not ok:
                n_fail += 1
                print(f"[{completed}/{len(jobs)}] FALLO {rho_label} eta={eta} rea={realization} "
                      f"seed={seed} (rc={result.returncode})")
                print(result.stdout, file=sys.stdout)
                print(result.stderr, file=sys.stderr)
            elif completed % 100 == 0 or completed == len(jobs):
                print(f"[{completed}/{len(jobs)}] OK (ultima: {rho_label} eta={eta} rea={realization}, {elapsed:.2f}s)")

            rows.append({
                "model": "voter",
                "rho_nominal": rho_nominal,
                "rho_label": rho_label,
                "N": n,
                "eta": eta,
                "eta_index": eta_index,
                "steps": args.steps,
                "base_seed": seed,
                "realization": realization,
                "returncode": result.returncode,
                "elapsed_s": round(elapsed, 4),
            })

    with manifest_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total_elapsed = time.time() - total_start
    print(f"\nManifiesto: {manifest_path}")
    print(f"Tiempo total: {total_elapsed:.1f}s, fallos: {n_fail}/{len(jobs)}")

    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
