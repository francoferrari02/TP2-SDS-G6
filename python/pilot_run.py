#!/usr/bin/env python3
"""Lanzador de corridas piloto para TP2 (etapa 5, exploratorio).

No es parte del motor ni del barrido definitivo: solo invoca el binario
`simulate` ya validado (build/simulate) muchas veces, con una grilla de
`eta` explícitamente etiquetada como piloto, y registra un manifiesto plano
de qué corrida corresponde a qué combinación (model, rho, eta, seed,
realización), para que el análisis pueda cruzar archivos con parámetros sin
tener que volver a parsear rutas.

Los datos crudos se escriben bajo data/pilots/<run_name>/ (ignorado por git,
ver .gitignore). Este script no decide nada por su cuenta: solo ejecuta la
grilla fija abajo y deja constancia de los comandos y tiempos.

Uso:
    python3 python/pilot_run.py [--run-name NOMBRE] [--steps N] [--dry-run]
"""

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIMULATE_BIN = REPO_ROOT / "build" / "simulate"

# Grilla piloto de eta: explícitamente exploratoria, no la grilla definitiva
# del barrido de producción (esa decisión sigue abierta en
# plan_desarrollo_tp2/DECISIONES_PENDIENTES.md). Elegida para cubrir todo el
# rango físicamente distinguible del ruido U[-eta/2,eta/2]: con eta=0 no hay
# ruido; con eta >= 2*pi (~6.283) el ruido ya cubre el círculo completo de
# forma uniforme, así que valores mayores no agregan un régimen distinto.
# Se muestrean 6 puntos razonablemente espaciados en ese rango para separar
# cualitativamente bajo ruido / ruido intermedio / ruido alto sin
# comprometerse todavía con una grilla fina (eso requeriría ya haber visto
# estos resultados preliminares).
ETA_GRID_PILOT = [0.0, 1.0, 2.0, 3.0, 4.0, 6.0]

# Densidades obligatorias únicamente. Las densidades bajas se resolvieron
# despues de este piloto historico como redondeo a N=32,16,11; ver
# DECISIONES_PENDIENTES.md.
RHO_GRID = [
    (2.0, 200, "rho_2"),
    (4.0, 400, "rho_4"),
    (8.0, 800, "rho_8"),
]

MODELS = ["vicsek", "voter"]

REALIZATIONS = [0, 1, 2]  # 3 realizaciones independientes por combinación (piloto, no definitivo)

MODEL_SEED_OFFSET = {"vicsek": 0, "voter": 50000}
RHO_SEED_OFFSET = {2.0: 0, 4.0: 10000, 8.0: 20000}


def seed_for(model: str, rho_nominal: float, eta_index: int, realization: int) -> int:
    """Esquema de semillas explícito y determinista para el piloto.

    seed = 800000 + offset(modelo) + offset(rho) + 100*indice_eta + realizacion

    No hay aleatoriedad en la elección de semillas: es una función pura de
    la combinación, así que el manifiesto y la línea de comandos alcanzan
    para reproducir cualquier corrida del piloto sin volver a correr todo el
    lote.
    """
    return 800000 + MODEL_SEED_OFFSET[model] + RHO_SEED_OFFSET[rho_nominal] + 100 * eta_index + realization


def build_command(output_dir: Path, model: str, rho_nominal: float, rho_label: str, n: int,
                   eta: float, steps: int, seed: int, realization: int) -> list:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="pilot_grid_1", help="subdirectorio bajo data/pilots/")
    parser.add_argument("--steps", type=int, default=600, help="pasos por corrida (piloto)")
    parser.add_argument("--dry-run", action="store_true", help="solo imprime los comandos, no ejecuta nada")
    args = parser.parse_args()

    if not SIMULATE_BIN.exists() and not args.dry_run:
        print(f"No se encontro el binario {SIMULATE_BIN}. Compilar primero con cmake --build build.",
              file=sys.stderr)
        return 1

    output_dir = REPO_ROOT / "data" / "pilots" / args.run_name
    summary_dir = REPO_ROOT / "data" / "summary"
    manifest_path = summary_dir / f"{args.run_name}_manifest.csv"
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)

    combos = []
    for model in MODELS:
        for rho_nominal, n, rho_label in RHO_GRID:
            for eta_index, eta in enumerate(ETA_GRID_PILOT):
                for realization in REALIZATIONS:
                    seed = seed_for(model, rho_nominal, eta_index, realization)
                    combos.append((model, rho_nominal, rho_label, n, eta, eta_index, seed, realization))

    print(f"Total de corridas piloto: {len(combos)} "
          f"({len(MODELS)} modelos x {len(RHO_GRID)} densidades x {len(ETA_GRID_PILOT)} etas x "
          f"{len(REALIZATIONS)} realizaciones), steps={args.steps}, output_dir={output_dir}")

    rows = []
    total_start = time.time()
    for i, (model, rho_nominal, rho_label, n, eta, eta_index, seed, realization) in enumerate(combos, start=1):
        cmd = build_command(output_dir, model, rho_nominal, rho_label, n, eta, args.steps, seed, realization)
        if args.dry_run:
            print(" ".join(cmd))
            continue

        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start
        ok = result.returncode == 0
        status = "OK" if ok else f"FALLO({result.returncode})"
        print(f"[{i}/{len(combos)}] {model} {rho_label} eta={eta} rea={realization} "
              f"seed={seed} -> {status} ({elapsed:.2f}s)")
        if not ok:
            print(result.stdout, file=sys.stdout)
            print(result.stderr, file=sys.stderr)

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

    if not args.dry_run:
        with manifest_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        total_elapsed = time.time() - total_start
        n_fail = sum(1 for r in rows if r["returncode"] != 0)
        print(f"\nManifiesto: {manifest_path}")
        print(f"Tiempo total: {total_elapsed:.1f}s, fallos: {n_fail}/{len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
