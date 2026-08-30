#!/usr/bin/env python3
"""Graficos del estudio fino de eta entre 0 y 0.2 (voter_eta_fine_lowrange_run.py).

Reutiliza las funciones de voter_eta_study_plot.py (mismo formato de
gráficos), pero grafica las 5 series temporales completas (todos los eta
finos entrán, no hace falta subconjunto porque ya son pocos) y con
steps=5000 en el eje x.

Uso:
    python3 python/voter_eta_fine_lowrange_plot.py
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


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def plot_va_vs_eta(by_combo_rows, out_path: Path):
    fig, ax = plt.subplots(figsize=(7, 5))
    for rho_label in RHO_LABELS_ORDER:
        rows = sorted(
            (r for r in by_combo_rows if r["rho_label"] == rho_label),
            key=lambda r: float(r["eta"]),
        )
        etas = [float(r["eta"]) for r in rows]
        va = [float(r["va_mean"]) for r in rows]
        err = [float(r["va_stdev_between_realizations"]) for r in rows]
        ax.errorbar(etas, va, yerr=err, marker="o", capsize=3, label=RHO_DISPLAY[rho_label])
    ax.set_xlabel("eta")
    ax.set_ylabel("<va> estacionario")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Votante: polarizacion estacionaria vs ruido, zona fina 0<=eta<=0.2 (R=20, steps=5000)")
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
    ax.set_title(f"Votante, {RHO_DISPLAY[rho_label]}: relajacion de va(t), zona fina 0<=eta<=0.2 (steps=5000)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="voter_eta_fine_lowrange_1")
    args = parser.parse_args()

    summary_dir = REPO_ROOT / "data" / "summary"
    by_combo_rows = read_csv_rows(summary_dir / f"{args.run_name}_by_combo.csv")
    series_rows = read_csv_rows(summary_dir / f"{args.run_name}_series_sampled.csv")

    out_dir = REPO_ROOT / "figures" / args.run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_va_vs_eta(by_combo_rows, out_dir / "va_vs_eta.png")
    for rho_label in RHO_LABELS_ORDER:
        plot_va_time_series(series_rows, rho_label, out_dir / f"va_t_{rho_label}.png")

    print(f"Graficos escritos en {out_dir.relative_to(REPO_ROOT)}/:")
    for p in sorted(out_dir.glob("*.png")):
        print(f"  {p.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
