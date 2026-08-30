#!/usr/bin/env python3
"""Refinamiento fino de la grilla de eta entre 0 y 0.2 (paso 0.05), para las
tres densidades obligatorias del votante (rho=2,4,8).

Motivo: con eta=0.2 (3000 pasos) la serie de va(t) todavia mostraba un pico
transitorio seguido de una caida hacia un valor mas bajo, sin asentarse del
todo (ver plan_desarrollo_tp2/05_pilotos_y_grilla_eta.md). Cerca de eta=0 el
ruido tarda mas en "erosionar" el casi-consenso que se forma al principio
por coarsening, asi que el tiempo de relajacion real puede ser mayor que en
eta=0.2. Por eso esta grilla fina usa una duracion mayor (steps=5000, no los
3000 del estudio principal) y vive en un directorio de piloto separado
(data/pilots/voter_eta_fine_lowrange_1/), con su propia identidad de
protocolo (distinta duracion = distinta identidad, no se mezcla con
voter_eta_study_1).

No incluye las densidades bajas de clusters (1/pi,1/(2pi),1/(3pi)): esta
grilla fina se pidio especificamente para las densidades obligatorias.

Uso:
    python3 python/voter_eta_fine_lowrange_run.py [--run-name NOMBRE]
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

ETA_GRID = [0.0, 0.05, 0.1, 0.15, 0.2]

RHO_GRID = [
    (2.0, 200, "rho_2"),
    (4.0, 400, "rho_4"),
    (8.0, 800, "rho_8"),
]

MODEL = "voter"

RHO_SEED_OFFSET = {2.0: 0, 4.0: 30000, 8.0: 60000}
SEED_BASE = 970000


def seed_for(rho_nominal: float, eta_index: int, realization: int) -> int:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="voter_eta_fine_lowrange_1")
    parser.add_argument("--steps", type=int, default=5000)
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

    combos = []
    for rho_nominal, n, rho_label in RHO_GRID:
        for eta_index, eta in enumerate(ETA_GRID):
            for realization in realizations:
                seed = seed_for(rho_nominal, eta_index, realization)
                combos.append((rho_nominal, rho_label, n, eta, eta_index, seed, realization))

    print(f"Total de corridas: {len(combos)} "
          f"(votante x {len(RHO_GRID)} densidades x {len(ETA_GRID)} etas finos x "
          f"{len(realizations)} realizaciones), steps={args.steps}, output_dir={output_dir}")

    if args.dry_run:
        for rho_nominal, rho_label, n, eta, eta_index, seed, realization in combos:
            cmd = build_command(output_dir, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
            print(" ".join(cmd))
        return 0

    jobs = []
    for rho_nominal, rho_label, n, eta, eta_index, seed, realization in combos:
        cmd = build_command(output_dir, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
        jobs.append((cmd, rho_label, eta, seed, realization))

    rows = []
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
            elif completed % 25 == 0 or completed == len(jobs):
                print(f"[{completed}/{len(jobs)}] OK (ultima: {rho_label} eta={eta} rea={realization}, {elapsed:.2f}s)")

            rows.append({
                "model": MODEL,
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
    print(f"Tiempo total: {total_elapsed:.1f}s, fallos: {n_fail}/{len(rows)}")

    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
