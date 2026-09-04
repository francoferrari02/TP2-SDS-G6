#!/usr/bin/env python3
"""Serie temporal fina va(t) del votante para eta={0.05,0.3,1}, rho=2.

Reanaliza directamente los observables.csv crudos ya existentes (sin volver a
correr el motor) de dos lotes de produccion ya validados:

  - final_fine_grid_steps3000_R20_v1: eta=0.05, eta=0.30 (voter, rho_2).
  - final_voter_base_coarse_v1: eta=1.00 (voter, rho_2).

Motivo de un script dedicado en vez de volver a llamar a pilot_analyze.py
sobre esos run_name completos: eso reescribiria *_series_sampled.csv para
las 36 combinaciones de cada lote con un stride distinto al que ya usan las
tablas consolidadas finales (final_voter_base_grid_steps3000_R20_v1), que se
arman leyendo esos mismos series_sampled.csv -- cambiar su stride
mezclaria resoluciones temporales distintas dentro de una misma tabla final.
Este script solo lee los observables.csv crudos y escribe una tabla nueva y
separada, sin tocar ninguna tabla ya versionada.

Salida: data/summary/voter_va_t_eta_0p05_0p3_1_v1_series_sampled.csv,
con --sample-stride 10 (300 puntos en 3000 pasos), mismo formato de columnas
que series_sampled.csv de pilot_analyze.py (va_mean, va_stdev entre las
R=20 realizaciones en cada instante t, etc.).

Uso:
    python3 python/voter_va_t_eta_0p05_0p3_1_analyze.py
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
RUN_NAME = "voter_va_t_eta_0p05_0p3_1_v1"
SAMPLE_STRIDE = 10

SOURCES = [
    ("final_fine_grid_steps3000_R20_v1", {0.05, 0.30}),
    ("final_voter_base_coarse_v1", {1.0}),
]
MODEL = "voter"
RHO_LABEL = "rho_2"


def eta_matches(eta: float, allowed) -> bool:
    return any(abs(eta - e) < 1e-6 for e in allowed)


def main() -> int:
    combos = {}
    for run_name, etas in SOURCES:
        run_dir = REPO_ROOT / "data" / "pilots" / run_name
        obs_files = sorted(run_dir.rglob("observables.csv"))
        if not obs_files:
            print(f"No se encontraron observables.csv bajo {run_dir}", file=sys.stderr)
            return 1
        for path in obs_files:
            metadata, rows = read_observables_csv(path)
            if metadata["model"] != MODEL or metadata["rho_label"] != RHO_LABEL:
                continue
            eta = float(metadata["eta"])
            if not eta_matches(eta, etas):
                continue
            problems = validate_observables(path, metadata, rows)
            if problems:
                print(f"{path}: {problems}", file=sys.stderr)
                return 1
            combos.setdefault(round(eta, 6), []).append(rows)

    expected_etas = {0.05, 0.30, 1.0}
    missing = expected_etas - set(combos.keys())
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
            if not va_vals:
                continue
            sample_r = len(va_vals)
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
