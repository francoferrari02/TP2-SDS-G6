#!/usr/bin/env python3
"""Lanzador de los puntos faltantes del votante en la grilla comun base.

Contexto: la grilla final comun aprobada
(eta={0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,1,2,3,4,5,6}) ya tiene, para el
votante y las densidades obligatorias rho=2,4,8, los puntos finos
{0.05,0.10,0.15,0.20,0.30,0.40} cubiertos por
final_fine_grid_steps3000_R20_v1 (steps=3000, R=20, t_eq=1500). Los estudios
voter_eta_study_1 (t_eq=2250), voter_lowrho_cluster_study_1 (t_eq=2250) y
voter_eta_fine_lowrange_1 (steps=5000) no son reutilizables como datos
finales porque usan un protocolo distinto (ver DECISIONES_PENDIENTES.md).
Este script cubre el resto de la grilla comun (los 8 puntos restantes) con
el protocolo final: steps=3000, R=20, t_eq=1500 (aplicado en el analisis),
sin trayectoria.

Sigue el patron de python/final_fine_grid_run.py, restringido al modelo
voter y a los 8 puntos de eta que faltan.

Uso:
    python3 python/final_voter_base_coarse_run.py [--run-name NOMBRE]
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

MODEL = "voter"
L = 10.0

# Puntos de la grilla comun de 14 que NO estan cubiertos por
# final_fine_grid_steps3000_R20_v1 (esa corrida ya cubrio 0.05..0.40).
ETA_GRID = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

RHO_GRID = [
    (2.0, 200, "rho_2"),
    (4.0, 400, "rho_4"),
    (8.0, 800, "rho_8"),
]

# Base de semilla nueva, elegida para no solaparse con ningun estudio previo:
# pilot_run.py (~800000-820000), voter_eta_study_run.py (900000+...),
# voter_lowrho_cluster_study_run.py (950000+...), voter_eta_fine_lowrange_run.py
# (970000+...), final_fine_grid_run.py (1100000-1260519),
# vicsek_lowrho_cluster_study_run.py (1250000-1291319). El maximo usado hasta
# ahora es 1291319; esta base arranca muy por encima de ese maximo.
SEED_BASE = 1400000
RHO_SEED_OFFSET = {2.0: 0, 4.0: 10000, 8.0: 20000}


def seed_for(rho_nominal: float, eta_index: int, realization: int) -> int:
    """seed = 1400000 + rho_offset + 100*eta_index + realizacion.

    Con 8 etas (indice 0..7) y realizacion 0..19, 100*eta_index+realizacion
    <= 719, muy por debajo del espaciado de 10000 entre densidades: sin
    colision posible entre combinaciones de este lote ni con lotes previos.
    """
    return SEED_BASE + RHO_SEED_OFFSET[rho_nominal] + 100 * eta_index + realization


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


def find_output_path(output_dir: Path, rho_label: str, steps: int, realization: int, seed: int) -> str:
    """Reconstruye la ruta real publicada por la CLI (ver compute_run_directory
    en src/cli/simulate_cli.hpp) buscando el directorio de la realizacion
    concreta, en vez de reimplementar el formateo de punto flotante de eta."""
    pattern = f"{MODEL}/{rho_label}/eta_*/steps_{steps}/realization_{realization:03d}_seed_{seed}"
    matches = sorted((output_dir).glob(pattern))
    if not matches:
        return ""
    return str(matches[0].relative_to(REPO_ROOT))


def build_combos(realizations):
    combos = []
    for rho_nominal, n, rho_label in RHO_GRID:
        for eta_index, eta in enumerate(ETA_GRID):
            for realization in realizations:
                seed = seed_for(rho_nominal, eta_index, realization)
                combos.append((rho_nominal, rho_label, n, eta, eta_index, seed, realization))
    return combos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="final_voter_base_coarse_v1")
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--realizations", type=int, default=20)
    parser.add_argument("--jobs", type=int, default=8, help="corridas en paralelo")
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

    expected = len(RHO_GRID) * len(ETA_GRID) * len(realizations)
    print(f"Total de corridas: {len(combos)} (esperado {expected}) "
          f"(voter x {len(RHO_GRID)} densidades x {len(ETA_GRID)} etas x "
          f"{len(realizations)} realizaciones), steps={args.steps}, output_dir={output_dir}")
    assert len(combos) == expected, "la cantidad de combinaciones no coincide con lo esperado"

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
            elif completed % 50 == 0 or completed == len(jobs):
                print(f"[{completed}/{len(jobs)}] OK (ultima: {rho_label} eta={eta} rea={realization}, {elapsed:.2f}s)")

            output_path = find_output_path(output_dir, rho_label, args.steps, realization, seed) if ok else ""
            rows.append({
                "model": MODEL,
                "rho_nominal": rho_nominal,
                "rho_label": rho_label,
                "rho_effective": n / (L * L),
                "N": n,
                "eta": eta,
                "eta_index": eta_index,
                "steps": args.steps,
                "base_seed": seed,
                "realization": realization,
                "returncode": result.returncode,
                "elapsed_s": round(elapsed, 4),
                "output_path": output_path,
            })

    rows.sort(key=lambda r: (r["rho_label"], r["eta_index"], r["realization"]))

    with manifest_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total_elapsed = time.time() - total_start
    print(f"\nManifiesto: {manifest_path}")
    print(f"Tiempo total: {total_elapsed:.1f}s, fallos: {n_fail}/{len(rows)}")

    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
