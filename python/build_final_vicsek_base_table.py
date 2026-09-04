#!/usr/bin/env python3
"""Consolida la tabla final de produccion de Vicsek para rho=2,4,8.

Combina, sin volver a correr nada, tres lotes ya validados:

  - final_fine_grid_steps3000_R20_v1 (filtrado a model=vicsek): cubre los
    puntos finos eta={0.05,0.10,0.15,0.20,0.30,0.40} de la grilla comun.
  - vicsek_eta0_6_deta0p5_steps3000_R20_v1 (filtrado a
    eta={0,0.5,1,2,3,4,5,6}): cubre los puntos enteros/medios de la grilla
    comun original de 14 puntos.
  - final_dense_eta_grid_steps3000_R20_v1 (filtrado a model=vicsek): cubre
    los 23 puntos nuevos con paso 0.2 entre eta=0.6 y eta=6.2, agregados el
    2026-09-03 porque la grilla de 14 puntos resultaba demasiado gruesa para
    las figuras finales de <va> vs. eta (ver DECISIONES_PENDIENTES.md).

Los tres lotes comparten protocolo (steps=3000, R=20, t_eq=1500, rho=2,4,8,
CIM, sin trayectoria), asi que la union cubre exactamente los 37 puntos de
la grilla comun ampliada sin superposicion. El script valida esto
explicitamente antes de escribir nada.

vicsek_eta0_6_deta0p5_steps3000_R20_v1 no tiene un manifiesto de lanzador
versionado (solo las tablas *_by_realization/_by_combo/_series_sampled).
Para esas filas, el manifiesto consolidado se reconstruye a partir de
*_by_realization.csv (que ya trae model, rho, N, eta, base_seed,
realization, steps): `returncode` se completa en 0 (las filas ya pasaron la
validacion de formato de pilot_analyze.py, que solo acepta observables.csv
completos y validos) y `elapsed_s` queda vacio porque ese dato nunca se
registro para ese lote historico.

Cada fila de las cuatro tablas de salida lleva una columna `source_run` que
identifica el lote de origen, para trazabilidad.

Salida (bajo data/summary/):
    final_vicsek_base_grid_steps3000_R20_v1_manifest.csv
    final_vicsek_base_grid_steps3000_R20_v1_by_realization.csv
    final_vicsek_base_grid_steps3000_R20_v1_by_combo.csv
    final_vicsek_base_grid_steps3000_R20_v1_series_sampled.csv

Uso:
    python3 python/build_final_vicsek_base_table.py
"""

import csv
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"

FINE_GRID_RUN = "final_fine_grid_steps3000_R20_v1"
FINE_GRID_ETAS = {0.05, 0.10, 0.15, 0.20, 0.30, 0.40}

WIDE_GRID_RUN = "vicsek_eta0_6_deta0p5_steps3000_R20_v1"
WIDE_GRID_ETAS = {0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0}

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

COMMON_GRID_ETAS = FINE_GRID_ETAS | WIDE_GRID_ETAS | DENSE_GRID_ETAS  # 37 puntos
RHO_LABELS = {"rho_2": 200, "rho_4": 400, "rho_8": 800}
EXPECTED_R = 20
EXPECTED_STEPS = 3000
EXPECTED_T_EQ = 1500

OUTPUT_RUN_NAME = "final_vicsek_base_grid_steps3000_R20_v1"


def read_csv(path: Path):
    with path.open() as f:
        return list(csv.DictReader(f))


def eta_matches(row_eta: str, allowed: set) -> bool:
    return any(abs(float(row_eta) - e) < 1e-6 for e in allowed)


def main() -> int:
    assert len(COMMON_GRID_ETAS) == 37, "la union de los tres lotes debe dar exactamente 37 puntos de eta"
    overlap_fw = FINE_GRID_ETAS & WIDE_GRID_ETAS
    overlap_fd = FINE_GRID_ETAS & DENSE_GRID_ETAS
    overlap_wd = WIDE_GRID_ETAS & DENSE_GRID_ETAS
    assert not overlap_fw, f"fine/wide no deberian superponerse en eta, pero comparten {overlap_fw}"
    assert not overlap_fd, f"fine/dense no deberian superponerse en eta, pero comparten {overlap_fd}"
    assert not overlap_wd, f"wide/dense no deberian superponerse en eta, pero comparten {overlap_wd}"

    # --- manifiesto ---
    fine_manifest = [r for r in read_csv(SUMMARY_DIR / f"{FINE_GRID_RUN}_manifest.csv")
                      if r["model"] == "vicsek" and eta_matches(r["eta"], FINE_GRID_ETAS)]
    for r in fine_manifest:
        r["source_run"] = FINE_GRID_RUN

    wide_by_real_for_manifest = [r for r in read_csv(SUMMARY_DIR / f"{WIDE_GRID_RUN}_by_realization.csv")
                                  if eta_matches(r["eta"], WIDE_GRID_ETAS)]
    wide_manifest = []
    for r in wide_by_real_for_manifest:
        wide_manifest.append({
            "model": r["model"],
            "rho_nominal": r["rho_nominal"],
            "rho_label": r["rho_label"],
            "N": r["N"],
            "eta": r["eta"],
            "eta_index": "",
            "steps": r["steps"],
            "base_seed": r["base_seed"],
            "realization": r["realization"],
            "returncode": 0,
            "elapsed_s": "",
            "source_run": WIDE_GRID_RUN,
        })

    dense_manifest = [r for r in read_csv(SUMMARY_DIR / f"{DENSE_GRID_RUN}_manifest.csv")
                       if r["model"] == "vicsek" and eta_matches(r["eta"], DENSE_GRID_ETAS)]
    for r in dense_manifest:
        r["source_run"] = DENSE_GRID_RUN

    manifest_fieldnames = ["model", "rho_nominal", "rho_label", "N", "eta", "eta_index",
                            "steps", "base_seed", "realization", "returncode", "elapsed_s", "source_run"]
    for r in fine_manifest:
        r.setdefault("eta_index", "")
    for r in dense_manifest:
        r.setdefault("eta_index", "")
    manifest_rows = fine_manifest + wide_manifest + dense_manifest

    # --- by_realization ---
    fine_by_real = [r for r in read_csv(SUMMARY_DIR / f"{FINE_GRID_RUN}_by_realization.csv")
                     if r["model"] == "vicsek" and eta_matches(r["eta"], FINE_GRID_ETAS)]
    for r in fine_by_real:
        r["source_run"] = FINE_GRID_RUN
    wide_by_real = [r for r in read_csv(SUMMARY_DIR / f"{WIDE_GRID_RUN}_by_realization.csv")
                     if eta_matches(r["eta"], WIDE_GRID_ETAS)]
    for r in wide_by_real:
        r["source_run"] = WIDE_GRID_RUN
    dense_by_real = [r for r in read_csv(SUMMARY_DIR / f"{DENSE_GRID_RUN}_by_realization.csv")
                      if r["model"] == "vicsek" and eta_matches(r["eta"], DENSE_GRID_ETAS)]
    for r in dense_by_real:
        r["source_run"] = DENSE_GRID_RUN
    by_realization_rows = fine_by_real + wide_by_real + dense_by_real

    # --- by_combo ---
    fine_by_combo = [r for r in read_csv(SUMMARY_DIR / f"{FINE_GRID_RUN}_by_combo.csv")
                      if r["model"] == "vicsek" and eta_matches(r["eta"], FINE_GRID_ETAS)]
    for r in fine_by_combo:
        r["source_run"] = FINE_GRID_RUN
    wide_by_combo = [r for r in read_csv(SUMMARY_DIR / f"{WIDE_GRID_RUN}_by_combo.csv")
                      if eta_matches(r["eta"], WIDE_GRID_ETAS)]
    for r in wide_by_combo:
        r["source_run"] = WIDE_GRID_RUN
    dense_by_combo = [r for r in read_csv(SUMMARY_DIR / f"{DENSE_GRID_RUN}_by_combo.csv")
                       if r["model"] == "vicsek" and eta_matches(r["eta"], DENSE_GRID_ETAS)]
    for r in dense_by_combo:
        r["source_run"] = DENSE_GRID_RUN
    by_combo_rows = fine_by_combo + wide_by_combo + dense_by_combo

    # --- series_sampled ---
    fine_series = [r for r in read_csv(SUMMARY_DIR / f"{FINE_GRID_RUN}_series_sampled.csv")
                   if r["model"] == "vicsek" and eta_matches(r["eta"], FINE_GRID_ETAS)]
    for r in fine_series:
        r["source_run"] = FINE_GRID_RUN
    wide_series = [r for r in read_csv(SUMMARY_DIR / f"{WIDE_GRID_RUN}_series_sampled.csv")
                   if eta_matches(r["eta"], WIDE_GRID_ETAS)]
    for r in wide_series:
        r["source_run"] = WIDE_GRID_RUN
    dense_series = [r for r in read_csv(SUMMARY_DIR / f"{DENSE_GRID_RUN}_series_sampled.csv")
                     if r["model"] == "vicsek" and eta_matches(r["eta"], DENSE_GRID_ETAS)]
    for r in dense_series:
        r["source_run"] = DENSE_GRID_RUN
    series_rows = fine_series + wide_series + dense_series

    # --- validaciones explicitas antes de escribir nada ---
    problems = []

    for r in by_realization_rows:
        if r["model"] != "vicsek":
            problems.append(f"by_realization: modelo no vicsek: {r}")
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

    # etas duplicados: para cada (rho_label, eta) la cantidad de filas debe ser R, ni mas ni menos
    # (ya cubierto por wrong_r), y ningun eta debe aparecer en ambos lotes de origen a la vez.
    seen_by_source = {}
    for r in by_realization_rows:
        key = (r["rho_label"], round(float(r["eta"]), 6))
        seen_by_source.setdefault(key, set()).add(r["source_run"])
    duplicated_sources = {k: v for k, v in seen_by_source.items() if len(v) > 1}
    if duplicated_sources:
        problems.append(f"combinaciones cubiertas por mas de un lote de origen (eta duplicado): {duplicated_sources}")

    seen_etas = sorted({round(float(r["eta"]), 6) for r in by_realization_rows})
    expected_etas_rounded = sorted({round(e, 6) for e in COMMON_GRID_ETAS})
    if seen_etas != expected_etas_rounded:
        problems.append(f"etas observados {seen_etas} != grilla comun esperada {expected_etas_rounded}")

    for r in by_realization_rows:
        va = float(r["va_window_mean"])
        s = float(r["S_window_mean"])
        if not (0.0 - 1e-9 <= va <= 1.0 + 1e-9) or not (0.0 - 1e-9 <= s <= 1.0 + 1e-9):
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

    if problems:
        print(f"{len(problems)} problema(s) encontrado(s), no se escribe ninguna tabla:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"Validacion OK: {len(by_realization_rows)} filas by_realization "
          f"({len(RHO_LABELS)} rho x {len(COMMON_GRID_ETAS)} eta x R={EXPECTED_R}), "
          f"{len(combo_counts)} combinaciones, todas con R={EXPECTED_R}.")

    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    def write(rows, suffix):
        path = SUMMARY_DIR / f"{OUTPUT_RUN_NAME}_{suffix}.csv"
        fieldnames = list(rows[0].keys())
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Escrito: {path.relative_to(REPO_ROOT)} ({len(rows)} filas)")

    manifest_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"]), int(r["realization"])))
    by_realization_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"]), int(r["realization"])))
    by_combo_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"])))
    series_rows.sort(key=lambda r: (r["rho_label"], float(r["eta"]), int(r["t"])))

    write(manifest_rows, "manifest")
    write(by_realization_rows, "by_realization")
    write(by_combo_rows, "by_combo")
    write(series_rows, "series_sampled")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
