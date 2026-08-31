#!/usr/bin/env python3
"""Lanzador de la grilla fina de produccion final, para ambos modelos.

Motivacion: las figuras finales C/D (<va> vs eta, <S> vs eta) necesitan una
grilla comun fina en la zona eta<=0.4 (donde el votante cambia rapido) para
ambos modelos, con el protocolo ya decidido en DECISIONES_PENDIENTES.md
(R=20 realizaciones, steps=3000, t_eq=1500). Esta grilla fina
{0.05,0.10,0.15,0.20,0.30,0.40} es un subconjunto de la grilla final de 14
puntos aprobada; no la reemplaza, es el bloque necesario para las figuras que
comparan ambos modelos en la zona de interes con la misma densidad de puntos.

Sigue el patron de python/voter_eta_study_run.py y
python/voter_eta_refine_run.py, generalizado a los dos modelos (vicsek y
voter) en un unico lanzamiento con manifiesto propio.

Uso:
    python3 python/final_fine_grid_run.py [--run-name NOMBRE] [--steps N]
        [--realizations N] [--jobs N] [--dry-run]
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

MODELS = ["vicsek", "voter"]

ETA_GRID = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]

RHO_GRID = [
    (2.0, 200, "rho_2"),
    (4.0, 400, "rho_4"),
    (8.0, 800, "rho_8"),
]

MODEL_SEED_OFFSET = {"vicsek": 0, "voter": 100000}
RHO_SEED_OFFSET = {2.0: 0, 4.0: 30000, 8.0: 60000}


def seed_for(model: str, rho_nominal: float, eta_index: int, realization: int) -> int:
    """Esquema de semillas explicito y determinista, sin colisiones.

    seed = 1100000 + model_offset + rho_offset + 100*eta_index + realizacion

    Con 6 valores de eta (indice 0..5) y realizacion 0..19,
    100*eta_index + realizacion <= 519, muy por debajo del espaciado de
    30000 entre densidades y de 100000 entre modelos: no hay colision
    posible entre combinaciones.
    """
    return (1100000 + MODEL_SEED_OFFSET[model] + RHO_SEED_OFFSET[rho_nominal]
            + 100 * eta_index + realization)


def build_command(output_dir: Path, model: str, rho_nominal: float, rho_label: str,
                   n: int, eta: float, steps: int, seed: int, realization: int) -> list:
    return [
        str(SIMULATE_BIN),
        "--model", model,
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
    for model in MODELS:
        for rho_nominal, n, rho_label in RHO_GRID:
            for eta_index, eta in enumerate(ETA_GRID):
                for realization in realizations:
                    seed = seed_for(model, rho_nominal, eta_index, realization)
                    combos.append((model, rho_nominal, rho_label, n, eta, eta_index, seed, realization))
    return combos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="final_fine_grid_steps3000_R20_v1")
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--realizations", type=int, default=20)
    parser.add_argument("--jobs", type=int, default=8, help="corridas en paralelo")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only-failed-from", type=Path, default=None,
                         help="manifiesto previo: repetir solo las corridas con returncode != 0")
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

    if args.only_failed_from is not None:
        failed_keys = set()
        with args.only_failed_from.open() as f:
            for row in csv.DictReader(f):
                if int(row["returncode"]) != 0:
                    failed_keys.add((row["model"], row["rho_label"], row["eta"], row["realization"]))
        combos = [c for c in combos if (c[0], c[2], repr(c[4]), str(c[7])) in failed_keys]
        print(f"Repitiendo solo corridas fallidas: {len(combos)}")

    print(f"Total de corridas: {len(combos)} "
          f"({len(MODELS)} modelos x {len(RHO_GRID)} densidades x {len(ETA_GRID)} etas x "
          f"{len(realizations)} realizaciones), steps={args.steps}, output_dir={output_dir}")

    if args.dry_run:
        for model, rho_nominal, rho_label, n, eta, eta_index, seed, realization in combos:
            cmd = build_command(output_dir, model, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
            print(" ".join(cmd))
        return 0

    jobs = []
    for model, rho_nominal, rho_label, n, eta, eta_index, seed, realization in combos:
        cmd = build_command(output_dir, model, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
        jobs.append((cmd, model, rho_nominal, rho_label, n, eta, eta_index, seed, realization))

    rows = []
    n_fail = 0
    total_start = time.time()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_one, job[0]): job for job in jobs}
        completed = 0
        for future, job in futures.items():
            result, elapsed = future.result()
            cmd, model, rho_nominal, rho_label, n, eta, eta_index, seed, realization = job
            completed += 1
            ok = result.returncode == 0
            if not ok:
                n_fail += 1
                print(f"[{completed}/{len(jobs)}] FALLO {model} {rho_label} eta={eta} rea={realization} "
                      f"seed={seed} (rc={result.returncode})")
                print(result.stdout, file=sys.stdout)
                print(result.stderr, file=sys.stderr)
            elif completed % 50 == 0 or completed == len(jobs):
                print(f"[{completed}/{len(jobs)}] OK (ultima: {model} {rho_label} eta={eta} rea={realization}, {elapsed:.2f}s)")

            rows.append({
                "model": model,
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

    # si es una repeticion parcial, mezclar con el manifiesto previo antes de escribir
    if args.only_failed_from is not None:
        previous_rows = []
        keys_updated = {(r["model"], r["rho_label"], repr(r["eta"]), str(r["realization"])) for r in rows}
        with args.only_failed_from.open() as f:
            for row in csv.DictReader(f):
                key = (row["model"], row["rho_label"], row["eta"], row["realization"])
                if key not in keys_updated:
                    previous_rows.append(row)
        rows = previous_rows + rows
        rows.sort(key=lambda r: (str(r["model"]), str(r["rho_label"]), float(r["eta"]), int(r["realization"])))

    with manifest_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total_elapsed = time.time() - total_start
    print(f"\nManifiesto: {manifest_path}")
    print(f"Tiempo total: {total_elapsed:.1f}s, fallos: {n_fail}/{len(jobs) if args.only_failed_from is None else len(rows)}")

    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
