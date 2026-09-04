#!/usr/bin/env python3
"""Consolida la tabla final de produccion del votante para rho=2,4,8.

Combina, sin volver a correr nada ni recomputar ningun valor, tres lotes ya
validados que comparten protocolo (steps=3000, R=20, t_eq=1500, rho=2,4,8,
CIM, sin trayectoria):

  - final_fine_grid_steps3000_R20_v1 (filtrado a model=voter): cubre los
    puntos finos eta={0.05,0.10,0.15,0.20,0.30,0.40} de la grilla comun.
  - final_voter_base_coarse_v1: cubre eta={0,0.50,1,2,3,4,5,6}.
  - final_dense_eta_grid_steps3000_R20_v1 (filtrado a model=voter): cubre
    los 23 puntos nuevos con paso 0.2 entre eta=0.6 y eta=6.2, agregados el
    2026-09-03 porque la grilla de 14 puntos resultaba demasiado gruesa para
    las figuras finales de <va> vs. eta (ver DECISIONES_PENDIENTES.md).

La union cubre exactamente los 37 puntos de la grilla comun ampliada, sin
solapamiento entre lotes. El script valida esto antes de escribir nada.

Los dos manifiestos de origen no tienen el mismo conjunto de columnas
(`final_voter_base_coarse_v1` agrega `rho_effective` y `output_path`). El
manifiesto consolidado usa la union de columnas y deja vacio lo que un lote
no registro; no se inventa ningun valor.

Cada fila de las cuatro tablas de salida lleva `source_run` para
trazabilidad.

Salida (bajo data/summary/):
    final_voter_base_grid_steps3000_R20_v1_manifest.csv
    final_voter_base_grid_steps3000_R20_v1_by_realization.csv
    final_voter_base_grid_steps3000_R20_v1_by_combo.csv
    final_voter_base_grid_steps3000_R20_v1_series_sampled.csv

Uso:
    python3 python/build_final_voter_base_table.py
"""

import csv
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"

FINE_GRID_RUN = "final_fine_grid_steps3000_R20_v1"
FINE_GRID_ETAS = {0.05, 0.10, 0.15, 0.20, 0.30, 0.40}

COARSE_RUN = "final_voter_base_coarse_v1"
COARSE_ETAS = {0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0}

DENSE_GRID_RUN = "final_dense_eta_grid_steps3000_R20_v1"
DENSE_GRID_ETAS = {
    0.60, 0.80,
    1.20, 1.40, 1.60, 1.80,
    2.20, 2.40, 2.60, 2.80,
    3.20, 3.40, 3.60, 3.80,
    4.20, 4.40, 4.60, 4.80,
    5.20, 5.40, 5.60, 5.80,
    6.20,
}

COMMON_GRID_ETAS = FINE_GRID_ETAS | COARSE_ETAS | DENSE_GRID_ETAS  # 37 puntos
RHO_LABELS = {"rho_2": 200, "rho_4": 400, "rho_8": 800}
EXPECTED_R = 20
EXPECTED_STEPS = 3000
EXPECTED_T_EQ = 1500

OUTPUT_RUN_NAME = "final_voter_base_grid_steps3000_R20_v1"

MANIFEST_FIELDNAMES = [
    "model", "rho_nominal", "rho_label", "rho_effective", "N", "eta", "eta_index",
    "steps", "base_seed", "realization", "returncode", "elapsed_s", "output_path",
    "source_run",
]


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def eta_matches(row_eta: str, allowed: set) -> bool:
    return any(abs(float(row_eta) - e) < 1e-6 for e in allowed)


def collect(suffix: str, model_filter: bool):
    """Devuelve las filas de ambos lotes para un sufijo de tabla, ya etiquetadas."""
    rows = []
    for run_name, etas in ((FINE_GRID_RUN, FINE_GRID_ETAS), (COARSE_RUN, COARSE_ETAS),
                           (DENSE_GRID_RUN, DENSE_GRID_ETAS)):
        for r in read_csv_rows(SUMMARY_DIR / f"{run_name}_{suffix}.csv"):
            if model_filter and r["model"] != "voter":
                continue
            if not eta_matches(r["eta"], etas):
                continue
            r["source_run"] = run_name
            rows.append(r)
    return rows


def main() -> int:
    assert len(COMMON_GRID_ETAS) == 37, "la union de los tres lotes debe dar exactamente 37 puntos de eta"
    overlap_fc = FINE_GRID_ETAS & COARSE_ETAS
    overlap_fd = FINE_GRID_ETAS & DENSE_GRID_ETAS
    overlap_cd = COARSE_ETAS & DENSE_GRID_ETAS
    assert not overlap_fc, f"fine/coarse no deberian superponerse en eta, pero comparten {overlap_fc}"
    assert not overlap_fd, f"fine/dense no deberian superponerse en eta, pero comparten {overlap_fd}"
    assert not overlap_cd, f"coarse/dense no deberian superponerse en eta, pero comparten {overlap_cd}"

    raw_manifest = collect("manifest", model_filter=True)
    manifest_rows = [{k: r.get(k, "") for k in MANIFEST_FIELDNAMES} for r in raw_manifest]
    by_realization_rows = collect("by_realization", model_filter=True)
    by_combo_rows = collect("by_combo", model_filter=True)
    series_rows = collect("series_sampled", model_filter=True)

    problems = []

    for r in by_realization_rows:
        if r["model"] != "voter":
            problems.append(f"by_realization: modelo no voter: {r}")
            break
    for r in by_realization_rows:
        if int(r["steps"]) != EXPECTED_STEPS:
            problems.append(f"by_realization: steps={r['steps']} != {EXPECTED_STEPS}")
            break
    for r in by_realization_rows:
        if int(r["t_window_start"]) != EXPECTED_T_EQ:
            problems.append(f"by_realization: t_window_start={r['t_window_start']} != {EXPECTED_T_EQ}")
            break
    for r in by_realization_rows:
        if r["rho_label"] not in RHO_LABELS:
            problems.append(f"by_realization: rho_label inesperado {r['rho_label']}")
            continue
        if int(r["N"]) != RHO_LABELS[r["rho_label"]]:
            problems.append(f"by_realization: N={r['N']} != {RHO_LABELS[r['rho_label']]} para {r['rho_label']}")

    expected_rows = len(RHO_LABELS) * len(COMMON_GRID_ETAS) * EXPECTED_R
    if len(by_realization_rows) != expected_rows:
        problems.append(f"by_realization: {len(by_realization_rows)} filas, esperaba {expected_rows}")

    combo_counts = Counter((r["rho_label"], round(float(r["eta"]), 6)) for r in by_realization_rows)
    expected_keys = {(rho, round(eta, 6)) for rho in RHO_LABELS for eta in COMMON_GRID_ETAS}
    observed_keys = set(combo_counts.keys())

    missing = expected_keys - observed_keys
    if missing:
        problems.append(f"combinaciones faltantes: {sorted(missing)}")
    extra = observed_keys - expected_keys
    if extra:
        problems.append(f"combinaciones no esperadas (posible fuga de otro eta/rho): {sorted(extra)}")
    wrong_r = {k: v for k, v in combo_counts.items() if v != EXPECTED_R}
    if wrong_r:
        problems.append(f"combinaciones sin exactamente R={EXPECTED_R} realizaciones: {wrong_r}")

    seen_by_source = {}
    for r in by_realization_rows:
        key = (r["rho_label"], round(float(r["eta"]), 6))
        seen_by_source.setdefault(key, set()).add(r["source_run"])
    duplicated_sources = {k: sorted(v) for k, v in seen_by_source.items() if len(v) > 1}
    if duplicated_sources:
        problems.append(f"combinaciones cubiertas por mas de un lote (eta duplicado): {duplicated_sources}")

    seen_etas = sorted({round(float(r["eta"]), 6) for r in by_realization_rows})
    expected_etas_rounded = sorted({round(e, 6) for e in COMMON_GRID_ETAS})
    if seen_etas != expected_etas_rounded:
        problems.append(f"etas observados {seen_etas} != grilla comun esperada {expected_etas_rounded}")

    for r in by_realization_rows:
        va = float(r["va_window_mean"])
        s = float(r["S_window_mean"])
        if not (-1e-9 <= va <= 1.0 + 1e-9) or not (-1e-9 <= s <= 1.0 + 1e-9):
            problems.append(f"va/S fuera de [0,1]: {r}")
            break

    if not by_combo_rows:
        problems.append("by_combo consolidado vacio")
    else:
        required_cols = {"va_stdev_between_realizations", "S_stdev_between_realizations"}
        missing_cols = required_cols - set(by_combo_rows[0].keys())
        if missing_cols:
            problems.append(f"by_combo: faltan columnas de desvio {sorted(missing_cols)}")
        expected_combo_rows = len(RHO_LABELS) * len(COMMON_GRID_ETAS)
        if len(by_combo_rows) != expected_combo_rows:
            problems.append(f"by_combo: {len(by_combo_rows)} filas, esperaba {expected_combo_rows}")
        for r in by_combo_rows:
            if int(r["realizations"]) != EXPECTED_R:
                problems.append(f"by_combo: realizations={r['realizations']} != {EXPECTED_R} en {r}")
                break

    if len(manifest_rows) != expected_rows:
        problems.append(f"manifest: {len(manifest_rows)} filas, esperaba {expected_rows}")

    if problems:
        print(f"{len(problems)} problema(s) encontrado(s), no se escribe ninguna tabla:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"Validacion OK: {len(by_realization_rows)} filas by_realization "
          f"({len(RHO_LABELS)} rho x {len(COMMON_GRID_ETAS)} eta x R={EXPECTED_R}), "
          f"{len(combo_counts)} combinaciones, todas con R={EXPECTED_R}, "
          f"steps={EXPECTED_STEPS}, t_window_start={EXPECTED_T_EQ}.")

    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    def write(rows, suffix, fieldnames=None):
        path = SUMMARY_DIR / f"{OUTPUT_RUN_NAME}_{suffix}.csv"
        names = fieldnames or list(rows[0].keys())
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=names, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Escrito: {path.relative_to(REPO_ROOT)} ({len(rows)} filas)")

    manifest_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"]), int(r["realization"])))
    by_realization_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"]), int(r["realization"])))
    by_combo_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"])))
    series_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"]), int(r["t"])))

    write(manifest_rows, "manifest", MANIFEST_FIELDNAMES)
    write(by_realization_rows, "by_realization")
    write(by_combo_rows, "by_combo")
    write(series_rows, "series_sampled")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
