#!/usr/bin/env python3
"""Gráficos diagnósticos del estudio de votante (voter_eta_study_run.py).

No son las figuras finales del informe (faltan t_eq definitivo, formato de
presentación, etc.): sirven para que el equipo pueda inspeccionar
visualmente la caída de <va> con eta y la relajación temporal, y así elegir
los casos característicos (ruido bajo / ruido alto) para animar.

Lee unicamente las tablas resumen ya generadas por
voter_eta_study_analyze.py (data/summary/voter_eta_study_1_*.csv); no vuelve
a tocar los observables.csv crudos.

Genera, bajo figures/voter_eta_study_1/:
  - va_vs_eta.png   : <va> estacionario vs eta, una curva por densidad, con
                      barras de error (desvio entre realizaciones).
  - S_vs_eta.png    : idem para <S>.
  - va_t_rho_2.png, va_t_rho_4.png, va_t_rho_8.png:
                      va(t) muestreado (promedio entre realizaciones +/- 1
                      desvio) para varios eta representativos de esa
                      densidad, para ver relajacion/transitorio.

Uso:
    python3 python/voter_eta_study_plot.py --run-name voter_eta_study_1
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent

RHO_LABELS_ORDER = ["rho_2", "rho_4", "rho_8"]
RHO_DISPLAY = {"rho_2": "rho=2", "rho_4": "rho=4", "rho_8": "rho=8"}

# Subconjunto de eta que se grafica en las series temporales por densidad,
# para no saturar el grafico con las 11 curvas del barrido completo.
SERIES_ETA_SUBSET = [0.0, 0.2, 0.5, 0.8, 1.5, 3.0, 6.0]


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def plot_va_vs_eta(by_combo_rows, out_path: Path, eta_max=None):
    fig, ax = plt.subplots(figsize=(7, 5))
    for rho_label in RHO_LABELS_ORDER:
        rows = sorted(
            (r for r in by_combo_rows if r["rho_label"] == rho_label
             and (eta_max is None or float(r["eta"]) <= eta_max)),
            key=lambda r: float(r["eta"]),
        )
        etas = [float(r["eta"]) for r in rows]
        va = [float(r["va_mean"]) for r in rows]
        err = [float(r["va_stdev_between_realizations"]) for r in rows]
        ax.errorbar(etas, va, yerr=err, marker="o", capsize=3, label=RHO_DISPLAY[rho_label])
    ax.set_xlabel("eta")
    ax.set_ylabel("<va> estacionario")
    ax.set_ylim(-0.05, 1.05)
    zoom_note = f" (zoom eta<= {eta_max:g})" if eta_max is not None else ""
    ax.set_title(f"Votante: polarizacion estacionaria vs ruido (R=20, barras = desvio entre realizaciones){zoom_note}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_s_vs_eta(by_combo_rows, out_path: Path, eta_max=None):
    fig, ax = plt.subplots(figsize=(7, 5))
    for rho_label in RHO_LABELS_ORDER:
        rows = sorted(
            (r for r in by_combo_rows if r["rho_label"] == rho_label
             and (eta_max is None or float(r["eta"]) <= eta_max)),
            key=lambda r: float(r["eta"]),
        )
        etas = [float(r["eta"]) for r in rows]
        s = [float(r["S_mean"]) for r in rows]
        err = [float(r["S_stdev_between_realizations"]) for r in rows]
        ax.errorbar(etas, s, yerr=err, marker="o", capsize=3, label=RHO_DISPLAY[rho_label])
    ax.set_xlabel("eta")
    ax.set_ylabel("<S> estacionario")
    ax.set_ylim(-0.05, 1.05)
    zoom_note = f" (zoom eta<= {eta_max:g})" if eta_max is not None else ""
    ax.set_title(f"Votante: fraccion del cluster mas grande vs ruido (R=20, barras = desvio entre realizaciones){zoom_note}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_va_time_series(series_rows, rho_label: str, out_path: Path):
    fig, ax = plt.subplots(figsize=(7, 5))
    by_eta = defaultdict(list)
    for row in series_rows:
        if row["rho_label"] != rho_label:
            continue
        eta = float(row["eta"])
        if not any(abs(eta - target) < 1e-9 for target in SERIES_ETA_SUBSET):
            continue
        by_eta[eta].append((int(row["t"]), float(row["va_mean"]), float(row["va_stdev"])))

    for eta in sorted(by_eta.keys()):
        points = sorted(by_eta[eta])
        ts = [p[0] for p in points]
        means = [p[1] for p in points]
        stds = [p[2] for p in points]
        ax.plot(ts, means, marker=".", markersize=3, label=f"eta={eta:g}")
        lower = [m - s for m, s in zip(means, stds)]
        upper = [m + s for m, s in zip(means, stds)]
        ax.fill_between(ts, lower, upper, alpha=0.15)

    ax.set_xlabel("paso t")
    ax.set_ylabel("va(t) (promedio entre realizaciones +/- 1 desvio)")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(f"Votante, {RHO_DISPLAY[rho_label]}: relajacion de va(t) para varios eta")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="voter_eta_study_1")
    args = parser.parse_args()

    summary_dir = REPO_ROOT / "data" / "summary"
    by_combo_rows = read_csv_rows(summary_dir / f"{args.run_name}_by_combo.csv")
    series_rows = read_csv_rows(summary_dir / f"{args.run_name}_series_sampled.csv")

    out_dir = REPO_ROOT / "figures" / args.run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_va_vs_eta(by_combo_rows, out_dir / "va_vs_eta.png")
    plot_s_vs_eta(by_combo_rows, out_dir / "S_vs_eta.png")
    # Version "zoom" (solo eta<=1.5, la zona densificada con la grilla
    # refinada): se guarda con nombre distinto para no pisar la version de
    # rango completo, asi se puede mostrar una al lado de la otra y
    # justificar por que se agrego resolucion ahi.
    plot_va_vs_eta(by_combo_rows, out_dir / "va_vs_eta_zoom_0_1.5.png", eta_max=1.5)
    plot_s_vs_eta(by_combo_rows, out_dir / "S_vs_eta_zoom_0_1.5.png", eta_max=1.5)
    for rho_label in RHO_LABELS_ORDER:
        plot_va_time_series(series_rows, rho_label, out_dir / f"va_t_{rho_label}.png")

    print(f"Graficos escritos en {out_dir.relative_to(REPO_ROOT)}/:")
    for p in sorted(out_dir.glob("*.png")):
        print(f"  {p.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
