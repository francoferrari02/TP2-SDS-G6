#!/usr/bin/env python3
"""Validacion programatica independiente de los lotes finales del votante.

No confia en pilot_analyze.py ni en los manifiestos de los lanzadores: relee
directamente las tablas *_by_realization.csv y *_by_combo.csv que ya
produjo pilot_analyze.py y comprueba, para cada lote pasado por
`--run-name`, exactamente lo que pide la tarea C de esta consolidacion:

  - cantidad exacta de corridas esperadas (segun la grilla declarada);
  - 20 realizaciones por combinacion;
  - steps=3000 en todas las filas;
  - t_window_start=1500 en todas las filas (ventana estacionaria t_eq);
  - etas exactos de la grilla declarada;
  - densidades (rho_label) y N correctos;
  - 0 <= va,S <= 1;
  - cero fallos (returncode==0 en el manifiesto del lanzador, si existe);
  - columnas de desvio estandar presentes en la tabla por combinacion.

Uso:
    python3 python/validate_final_voter_matrix.py \\
        --run-name final_voter_base_coarse_v1 \\
        --expected-eta 0,0.5,1,2,3,4,5,6 \\
        --expected-rho rho_2:200,rho_4:400,rho_8:800 \\
        --expected-realizations 20 --expected-steps 3000 --expected-t-eq 1500

    python3 python/validate_final_voter_matrix.py \\
        --run-name final_voter_lowrho_grid_v1 \\
        --expected-eta 0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,1,2,3,4,5,6 \\
        --expected-rho rho_1_over_pi:32,rho_1_over_2pi:16,rho_1_over_3pi:11 \\
        --expected-realizations 20 --expected-steps 3000 --expected-t-eq 1500
"""

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_eta_list(text: str):
    return [float(x) for x in text.split(",")]


def parse_rho_map(text: str):
    result = {}
    for item in text.split(","):
        label, n = item.split(":")
        result[label] = int(n)
    return result


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--expected-eta", required=True, help="lista separada por comas")
    parser.add_argument("--expected-rho", required=True,
                         help="rho_label:N separados por coma, p.ej. rho_2:200,rho_4:400")
    parser.add_argument("--expected-realizations", type=int, required=True)
    parser.add_argument("--expected-steps", type=int, required=True)
    parser.add_argument("--expected-t-eq", type=int, required=True)
    parser.add_argument("--expected-model", default="voter")
    args = parser.parse_args()

    expected_etas = parse_eta_list(args.expected_eta)
    expected_rho = parse_rho_map(args.expected_rho)
    expected_runs = len(expected_etas) * len(expected_rho) * args.expected_realizations

    summary_dir = REPO_ROOT / "data" / "summary"
    manifest_path = summary_dir / f"{args.run_name}_manifest.csv"
    by_realization_path = summary_dir / f"{args.run_name}_by_realization.csv"
    by_combo_path = summary_dir / f"{args.run_name}_by_combo.csv"

    problems = []

    # --- manifiesto del lanzador: cero fallos, cantidad exacta ---
    if manifest_path.exists():
        with manifest_path.open() as f:
            manifest_rows = list(csv.DictReader(f))
        if len(manifest_rows) != expected_runs:
            problems.append(f"manifiesto: {len(manifest_rows)} filas, esperaba {expected_runs}")
        n_fail = sum(1 for r in manifest_rows if int(r["returncode"]) != 0)
        if n_fail:
            problems.append(f"manifiesto: {n_fail} corridas con returncode != 0")
    else:
        problems.append(f"no se encontro el manifiesto {manifest_path}")

    # --- by_realization.csv: cantidad exacta, steps, t_eq, va/S en rango ---
    if not by_realization_path.exists():
        problems.append(f"no se encontro {by_realization_path}")
        by_real_rows = []
    else:
        with by_realization_path.open() as f:
            by_real_rows = list(csv.DictReader(f))

    if len(by_real_rows) != expected_runs:
        problems.append(f"by_realization: {len(by_real_rows)} filas, esperaba {expected_runs}")

    for row in by_real_rows:
        if row["model"] != args.expected_model:
            problems.append(f"by_realization: modelo inesperado {row['model']} en {row}")
            break
    for row in by_real_rows:
        if int(row["steps"]) != args.expected_steps:
            problems.append(f"by_realization: steps={row['steps']} distinto de {args.expected_steps}")
            break
    for row in by_real_rows:
        if int(row["t_window_start"]) != args.expected_t_eq:
            problems.append(f"by_realization: t_window_start={row['t_window_start']} distinto de {args.expected_t_eq}")
            break
    for row in by_real_rows:
        va = float(row["va_window_mean"])
        s = float(row["S_window_mean"])
        if not (0.0 - 1e-9 <= va <= 1.0 + 1e-9):
            problems.append(f"by_realization: va_window_mean fuera de [0,1]: {row}")
            break
    for row in by_real_rows:
        s = float(row["S_window_mean"])
        if not (0.0 - 1e-9 <= s <= 1.0 + 1e-9):
            problems.append(f"by_realization: S_window_mean fuera de [0,1]: {row}")
            break
    for row in by_real_rows:
        rho_label = row["rho_label"]
        if rho_label not in expected_rho:
            problems.append(f"by_realization: rho_label inesperado {rho_label}")
            continue
        if int(row["N"]) != expected_rho[rho_label]:
            problems.append(f"by_realization: N={row['N']} distinto de {expected_rho[rho_label]} para {rho_label}")

    seen_etas = sorted({round(float(r["eta"]), 9) for r in by_real_rows})
    expected_etas_rounded = sorted({round(e, 9) for e in expected_etas})
    if seen_etas != expected_etas_rounded:
        problems.append(f"etas observados {seen_etas} != etas esperados {expected_etas_rounded}")

    # --- realizaciones por combinacion ---
    from collections import Counter
    combo_counts = Counter((r["rho_label"], round(float(r["eta"]), 9)) for r in by_real_rows)
    expected_combo_keys = {(rho_label, round(eta, 9)) for rho_label in expected_rho for eta in expected_etas}
    missing_combos = expected_combo_keys - set(combo_counts.keys())
    if missing_combos:
        problems.append(f"combinaciones faltantes: {sorted(missing_combos)}")
    wrong_r = {k: v for k, v in combo_counts.items() if v != args.expected_realizations}
    if wrong_r:
        problems.append(f"combinaciones sin exactamente {args.expected_realizations} realizaciones: {wrong_r}")

    # --- by_combo.csv: columnas de desvio estandar presentes ---
    if not by_combo_path.exists():
        problems.append(f"no se encontro {by_combo_path}")
    else:
        with by_combo_path.open() as f:
            by_combo_rows = list(csv.DictReader(f))
        if not by_combo_rows:
            problems.append(f"{by_combo_path} esta vacio")
        else:
            required_cols = {"va_stdev_between_realizations", "S_stdev_between_realizations"}
            missing_cols = required_cols - set(by_combo_rows[0].keys())
            if missing_cols:
                problems.append(f"by_combo.csv: faltan columnas {sorted(missing_cols)}")
            expected_combos = len(expected_rho) * len(expected_etas)
            if len(by_combo_rows) != expected_combos:
                problems.append(f"by_combo: {len(by_combo_rows)} filas, esperaba {expected_combos}")
            for row in by_combo_rows:
                if int(row["realizations"]) != args.expected_realizations:
                    problems.append(f"by_combo: realizations={row['realizations']} distinto de {args.expected_realizations} en {row}")
                    break

    print(f"Validacion de {args.run_name}: {len(by_real_rows)} filas by_realization, "
          f"{len(combo_counts)} combinaciones observadas (esperadas {len(expected_combo_keys)}).")

    if problems:
        print(f"\n{len(problems)} problema(s) encontrado(s):")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("OK: sin problemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
