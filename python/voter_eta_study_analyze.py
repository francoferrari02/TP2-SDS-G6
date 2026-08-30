#!/usr/bin/env python3
"""Lector y resumen independiente del estudio dedicado del votante.

Misma lógica que pilot_analyze.py (relee cada observables.csv de forma
independiente, sin confiar en el manifiesto del lanzador, valida invariantes
de formato), aplicada al estudio de voter_eta_study_run.py: votante,
steps=3000, R=20, grilla de eta refinada {0,0.5,...,4,5,6}.

Produce, bajo data/summary/:
  - <run_name>_by_realization.csv: una fila por corrida, con la ventana
    estacionaria (últimos 25% de pasos) y su media/desvío temporal.
  - <run_name>_by_combo.csv: agregado entre las R realizaciones por
    (model, rho_label, eta): <va>, desvío entre realizaciones, error
    estándar, ídem para S, y una estimación heurística preliminar de t_eq.
  - <run_name>_series_sampled.csv: evolución temporal de va(t) promediada
    entre realizaciones, muestreada cada --sample-stride pasos.

Uso:
    python3 python/voter_eta_study_analyze.py --run-name voter_eta_study_1
"""

import argparse
import csv
import math
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_observables_csv(path: Path):
    metadata = {}
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        lines = f.readlines()

    header_index = None
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if stripped.startswith("#"):
            content = stripped[1:].strip()
            if "=" in content:
                key, _, value = content.partition("=")
                metadata[key.strip()] = value.strip()
            continue
        header_index = i
        break

    if header_index is None:
        raise ValueError(f"{path}: no se encontro linea de encabezado tras los comentarios.")

    reader = csv.DictReader(lines[header_index:])
    for record in reader:
        rows.append({
            "t": int(record["t"]),
            "va": float(record["va"]),
            "S": float(record["S"]),
        })
    return metadata, rows


def validate_observables(path: Path, metadata: dict, rows: list) -> list:
    problems = []
    if not rows:
        problems.append("sin filas de datos")
        return problems

    ts = [r["t"] for r in rows]
    if ts != sorted(ts):
        problems.append("t no esta ordenado")
    if ts[0] != 0:
        problems.append(f"falta t=0 (primer t={ts[0]})")

    expected_steps = int(metadata.get("steps", "-1"))
    if expected_steps >= 0 and ts[-1] != expected_steps:
        problems.append(f"falta el paso final t={expected_steps} (ultimo t={ts[-1]})")

    for r in rows:
        if not (0.0 - 1e-9 <= r["va"] <= 1.0 + 1e-9):
            problems.append(f"va fuera de [0,1] en t={r['t']}: {r['va']}")
            break
    for r in rows:
        if not (0.0 - 1e-9 <= r["S"] <= 1.0 + 1e-9):
            problems.append(f"S fuera de [0,1] en t={r['t']}: {r['S']}")
            break

    required_keys = {"model", "rho_label", "rho_nominal", "N", "eta", "base_seed",
                      "realization", "steps", "observables_stride"}
    missing = required_keys - metadata.keys()
    if missing:
        problems.append(f"metadatos faltantes: {sorted(missing)}")

    return problems


def stationary_window_stats(rows: list, fraction: float = 0.25):
    """Media y desvio temporal de va/S en el ultimo `fraction` de los pasos.

    Igual que en pilot_analyze.py: NO es una estimacion definitiva de t_eq,
    es un resumen provisional (ultimo cuarto de la corrida) para comparar
    entre combinaciones. t_eq real se decide mirando la serie completa.
    """
    t_max = rows[-1]["t"]
    t_start = t_max - int(round(fraction * t_max))
    window = [r for r in rows if r["t"] >= t_start]
    va_vals = [r["va"] for r in window]
    s_vals = [r["S"] for r in window]
    return {
        "t_window_start": t_start,
        "va_window_mean": statistics.fmean(va_vals),
        "va_window_stdev": statistics.pstdev(va_vals) if len(va_vals) > 1 else 0.0,
        "S_window_mean": statistics.fmean(s_vals),
        "S_window_stdev": statistics.pstdev(s_vals) if len(s_vals) > 1 else 0.0,
    }


def estimate_t_eq_heuristic(mean_series: list, final_mean: float, tolerance: float = 0.03):
    ts = [t for t, _ in mean_series]
    vals = [v for _, v in mean_series]
    n = len(vals)
    for i in range(n):
        if all(abs(vals[j] - final_mean) < tolerance for j in range(i, n)):
            return ts[i]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="voter_eta_study_1")
    parser.add_argument("--sample-stride", type=int, default=50,
                         help="cada cuantos pasos muestrear la serie temporal en el resumen")
    args = parser.parse_args()

    run_dir = REPO_ROOT / "data" / "pilots" / args.run_name
    summary_dir = REPO_ROOT / "data" / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    obs_files = sorted(run_dir.rglob("observables.csv"))
    if not obs_files:
        print(f"No se encontraron observables.csv bajo {run_dir}")
        return 1

    per_realization_rows = []
    problems_found = {}
    combos = {}

    for path in obs_files:
        metadata, rows = read_observables_csv(path)
        problems = validate_observables(path, metadata, rows)
        if problems:
            problems_found[str(path.relative_to(REPO_ROOT))] = problems
            continue

        stats = stationary_window_stats(rows)
        model = metadata["model"]
        rho_label = metadata["rho_label"]
        rho_nominal = metadata["rho_nominal"]
        n = metadata["N"]
        eta = metadata["eta"]
        seed = metadata["base_seed"]
        realization = metadata["realization"]
        steps = metadata["steps"]

        per_realization_rows.append({
            "model": model, "rho_label": rho_label, "rho_nominal": rho_nominal, "N": n,
            "eta": eta, "base_seed": seed, "realization": realization, "steps": steps,
            "va_t0": rows[0]["va"], "S_t0": rows[0]["S"],
            **stats,
        })

        combo_key = (model, rho_label, eta)
        combos.setdefault(combo_key, []).append((metadata, rows, stats))

    if not per_realization_rows:
        print("Ningun archivo valido; no se generan tablas.")
        for path, probs in problems_found.items():
            print(f"  {path}: {probs}")
        return 1

    by_realization_path = summary_dir / f"{args.run_name}_by_realization.csv"
    with by_realization_path.open("w", newline="") as f:
        fieldnames = list(per_realization_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(per_realization_rows)

    by_combo_rows = []
    series_rows = []
    for (model, rho_label, eta), entries in sorted(combos.items(), key=lambda kv: (kv[0][1], float(kv[0][2]))):
        va_means = [e[2]["va_window_mean"] for e in entries]
        s_means = [e[2]["S_window_mean"] for e in entries]
        r = len(entries)
        va_mean = statistics.fmean(va_means)
        va_std = statistics.stdev(va_means) if r > 1 else 0.0
        s_mean = statistics.fmean(s_means)
        s_std = statistics.stdev(s_means) if r > 1 else 0.0

        _, rows0, _ = entries[0]
        t_values = [r_["t"] for r_ in rows0 if r_["t"] % args.sample_stride == 0]
        if rows0[-1]["t"] not in t_values:
            t_values.append(rows0[-1]["t"])

        mean_series_va = []
        for t in t_values:
            vals = []
            for _, rows, _ in entries:
                match = next((row["va"] for row in rows if row["t"] == t), None)
                if match is not None:
                    vals.append(match)
            if vals:
                mean_series_va.append((t, statistics.fmean(vals)))
                series_rows.append({
                    "model": model, "rho_label": rho_label, "eta": eta, "t": t,
                    "va_mean": statistics.fmean(vals),
                    "va_stdev": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                })

        t_eq_estimate = estimate_t_eq_heuristic(mean_series_va, va_mean)

        by_combo_rows.append({
            "model": model, "rho_label": rho_label, "eta": eta, "realizations": r,
            "va_mean": va_mean, "va_stdev_between_realizations": va_std,
            "va_stderr": va_std / math.sqrt(r) if r > 1 else 0.0,
            "S_mean": s_mean, "S_stdev_between_realizations": s_std,
            "S_stderr": s_std / math.sqrt(r) if r > 1 else 0.0,
            "t_eq_heuristic_estimate": t_eq_estimate if t_eq_estimate is not None else "sin_evidencia",
        })

    by_combo_path = summary_dir / f"{args.run_name}_by_combo.csv"
    with by_combo_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(by_combo_rows[0].keys()))
        writer.writeheader()
        writer.writerows(by_combo_rows)

    series_path = summary_dir / f"{args.run_name}_series_sampled.csv"
    with series_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(series_rows[0].keys()))
        writer.writeheader()
        writer.writerows(series_rows)

    print(f"Archivos leidos: {len(obs_files)}, validos: {len(per_realization_rows)}, "
          f"con problemas: {len(problems_found)}")
    if problems_found:
        print("\nProblemas encontrados:")
        for path, probs in problems_found.items():
            print(f"  {path}: {probs}")

    print(f"\nEscrito: {by_realization_path.relative_to(REPO_ROOT)}")
    print(f"Escrito: {by_combo_path.relative_to(REPO_ROOT)}")
    print(f"Escrito: {series_path.relative_to(REPO_ROOT)}")

    return 1 if problems_found else 0


if __name__ == "__main__":
    raise SystemExit(main())
