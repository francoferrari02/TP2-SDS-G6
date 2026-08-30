#!/usr/bin/env python3
"""Lector y resumen independiente de los observables.csv de un piloto.

No confía en el manifiesto del lanzador: recorre los observables.csv reales
bajo data/pilots/<run_name>/, parsea la cabecera de metadatos (# clave=valor)
y los datos, y por sí solo verifica invariantes básicas del formato (t
ordenado, va/S en [0,1], t=0 y t=steps presentes). Esto es intencional: la
lectura debe funcionar igual si alguien mueve o copia un solo archivo, sin
depender del script que lo generó (ver contrato del formato en
plan_desarrollo_tp2/DECISIONES_PENDIENTES.md).

Produce:
  - data/summary/<run_name>_by_realization.csv: una fila por corrida, con
    valores iniciales, la ventana estacionaria propuesta (últimos 25% de
    pasos) y su media/desvío temporal.
  - data/summary/<run_name>_by_combo.csv: agregado entre realizaciones por
    (model, rho_label, eta): <va>, desvio entre realizaciones, error
    estandar, idem para S, y una estimacion preliminar de t_eq.
  - data/summary/<run_name>_series_sampled.csv: la evolucion temporal
    muestreada (cada `--sample-stride` pasos) de va(t)/S(t) promediada entre
    realizaciones, por combinacion -- para poder graficar o inspeccionar la
    relajacion sin tener que abrir los CSV crudos.

Estas tres tablas son las que se versionan en el repositorio; los
observables.csv crudos quedan fuera de git (data/pilots/ esta en
.gitignore).

Uso:
    python3 python/pilot_analyze.py --run-name pilot_grid_1
"""

import argparse
import csv
import math
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_observables_csv(path: Path):
    """Parsea un observables.csv de forma independiente del escritor.

    Devuelve (metadata: dict[str,str], rows: list[dict]).
    No asume nada del programa que lo genero: solo que las lineas de
    comentario empiezan con '#', que la primera linea sin '#' es el
    encabezado, y que el resto son filas CSV separadas por coma.
    """
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
    """Devuelve una lista de problemas encontrados (vacia si todo OK)."""
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

    Esta ventana NO es una estimacion definitiva de t_eq: es simplemente
    "el ultimo cuarto de la corrida", usada como resumen provisional para
    comparar entre combinaciones. La eleccion real de t_eq se discute con
    las series completas (ver tabla *_series_sampled.csv y el documento de
    pilotos), no con este numero solo.
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
    """Estimacion preliminar (no algoritmo de cierre) de cuando 'va' promedio
    entre realizaciones deja de alejarse de su valor final.

    Regla simple y documentada: recorrer los puntos muestreados en orden
    creciente de t y devolver el primer t tal que, para TODOS los puntos
    muestreados desde ese t en adelante, el valor este a una distancia
    absoluta menor a `tolerance` del promedio de la ventana final. Si
    ningun punto cumple esa condicion, se devuelve None (no hay evidencia
    suficiente en esta corrida para proponer t_eq).
    """
    ts = [t for t, _ in mean_series]
    vals = [v for _, v in mean_series]
    n = len(vals)
    for i in range(n):
        if all(abs(vals[j] - final_mean) < tolerance for j in range(i, n)):
            return ts[i]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="pilot_grid_1")
    parser.add_argument("--sample-stride", type=int, default=25,
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
    # combo_key -> list of (metadata, rows)
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

    # --- tabla por realizacion ---
    by_realization_path = summary_dir / f"{args.run_name}_by_realization.csv"
    with by_realization_path.open("w", newline="") as f:
        fieldnames = list(per_realization_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(per_realization_rows)

    # --- tabla por combinacion (agregada entre realizaciones) + series muestreadas ---
    by_combo_rows = []
    series_rows = []
    for (model, rho_label, eta), entries in sorted(combos.items()):
        va_means = [e[2]["va_window_mean"] for e in entries]
        s_means = [e[2]["S_window_mean"] for e in entries]
        r = len(entries)
        va_mean = statistics.fmean(va_means)
        va_std = statistics.stdev(va_means) if r > 1 else 0.0
        s_mean = statistics.fmean(s_means)
        s_std = statistics.stdev(s_means) if r > 1 else 0.0

        # serie temporal promedio entre realizaciones, muestreada cada
        # sample-stride pasos (todas las realizaciones de un combo tienen
        # el mismo steps/stride en este piloto, asi que comparten grilla de t).
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
