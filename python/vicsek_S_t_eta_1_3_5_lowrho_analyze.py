#!/usr/bin/env python3
"""Serie temporal fina S(t) de Vicsek para eta={1,3,5}, rho=1/pi (N=32).

Reanaliza directamente los observables.csv crudos ya existentes (sin volver a
correr el motor) del lote ya validado vicsek_lowrho_cluster_study_1
(rho_1_over_pi, N=32, R=20, steps=3000, grilla comun de 14 puntos de eta).

Igual que voter_va_t_eta_0p05_0p3_1_analyze.py: se escribe una tabla nueva y
separada con un --sample-stride mas fino que el de la tabla ya versionada
(vicsek_lowrho_cluster_study_1_series_sampled.csv, stride=50), sin tocar esa
tabla ni ninguna otra ya consolidada.

Salida: data/summary/vicsek_S_t_eta_1_3_5_lowrho_v1_series_sampled.csv,
con --sample-stride 10 (300 puntos en 3000 pasos).

Uso:
    python3 python/vicsek_S_t_eta_1_3_5_lowrho_analyze.py
"""

import csv
import math
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "python"))
from pilot_analyze import read_observables_csv, validate_observables  # noqa: E402

SUMMARY_DIR = REPO_ROOT / "data" / "summary"
RUN_NAME = "vicsek_S_t_eta_1_3_5_lowrho_v1"
SAMPLE_STRIDE = 10

SOURCE_RUN = "vicsek_lowrho_cluster_study_1"
MODEL = "vicsek"
RHO_LABEL = "rho_1_over_pi"
TARGET_ETAS = {1.0, 3.0, 5.0}


def eta_matches(eta: float) -> bool:
    return any(abs(eta - e) < 1e-6 for e in TARGET_ETAS)


def main() -> int:
    run_dir = REPO_ROOT / "data" / "pilots" / SOURCE_RUN
    obs_files = sorted(run_dir.rglob("observables.csv"))
    if not obs_files:
        print(f"No se encontraron observables.csv bajo {run_dir}", file=sys.stderr)
        return 1

    combos = {}
    for path in obs_files:
        metadata, rows = read_observables_csv(path)
        if metadata["model"] != MODEL or metadata["rho_label"] != RHO_LABEL:
            continue
        eta = float(metadata["eta"])
        if not eta_matches(eta):
            continue
        problems = validate_observables(path, metadata, rows)
        if problems:
            print(f"{path}: {problems}", file=sys.stderr)
            return 1
        combos.setdefault(round(eta, 6), []).append(rows)

    missing = TARGET_ETAS - set(combos.keys())
    if missing:
        print(f"Faltan combinaciones eta={sorted(missing)}", file=sys.stderr)
        return 1
    for eta, entries in combos.items():
        if len(entries) != 20:
            print(f"eta={eta}: {len(entries)} realizaciones, esperaba 20", file=sys.stderr)
            return 1

    series_rows = []
    for eta in sorted(combos.keys()):
        entries = combos[eta]
        rows0 = entries[0]
        t_values = [r["t"] for r in rows0 if r["t"] % SAMPLE_STRIDE == 0]
        if rows0[-1]["t"] not in t_values:
            t_values.append(rows0[-1]["t"])

        for t in t_values:
            va_vals, s_vals = [], []
            for rows in entries:
                match = next((r for r in rows if r["t"] == t), None)
                if match is not None:
                    va_vals.append(match["va"])
                    s_vals.append(match["S"])
            if not s_vals:
                continue
            sample_r = len(s_vals)
            va_stdev = statistics.pstdev(va_vals) if sample_r > 1 else 0.0
            s_stdev = statistics.pstdev(s_vals) if sample_r > 1 else 0.0
            series_rows.append({
                "model": MODEL, "rho_label": RHO_LABEL, "eta": eta, "t": t,
                "realizations": sample_r,
                "va_mean": statistics.fmean(va_vals),
                "va_stdev": va_stdev,
                "va_stderr": va_stdev / math.sqrt(sample_r) if sample_r > 1 else 0.0,
                "S_mean": statistics.fmean(s_vals),
                "S_stdev": s_stdev,
                "S_stderr": s_stdev / math.sqrt(sample_r) if sample_r > 1 else 0.0,
            })

    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SUMMARY_DIR / f"{RUN_NAME}_series_sampled.csv"
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(series_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(series_rows)

    print(f"Escrito: {out_path.relative_to(REPO_ROOT)} ({len(series_rows)} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
