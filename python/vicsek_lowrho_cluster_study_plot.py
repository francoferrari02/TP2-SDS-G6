#!/usr/bin/env python3
"""Graficos diagnosticos de clusters de Vicsek con densidades bajas."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent

RHO_LABELS_ORDER = ["rho_1_over_pi", "rho_1_over_2pi", "rho_1_over_3pi"]
RHO_DISPLAY = {
    "rho_1_over_pi": "rho=1/pi (N=32)",
    "rho_1_over_2pi": "rho=1/(2pi) (N=16)",
    "rho_1_over_3pi": "rho=1/(3pi) (N=11)",
}
SERIES_ETA_SUBSET = [0.0, 0.2, 0.5, 1.0, 3.0, 6.0]


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def plot_metric_vs_eta(by_combo_rows, mean_key: str, err_key: str, title: str, ylabel: str,
                       out_path: Path, eta_max=None):
    fig, ax = plt.subplots(figsize=(7, 5))
    for rho_label in RHO_LABELS_ORDER:
        rows = sorted(
            (r for r in by_combo_rows if r["rho_label"] == rho_label
             and (eta_max is None or float(r["eta"]) <= eta_max)),
            key=lambda r: float(r["eta"]),
        )
        etas = [float(r["eta"]) for r in rows]
        vals = [float(r[mean_key]) for r in rows]
        err = [float(r[err_key]) for r in rows]
        ax.errorbar(etas, vals, yerr=err, marker="o", capsize=3, label=RHO_DISPLAY[rho_label])
    ax.set_xlabel("eta")
    ax.set_ylabel(ylabel)
    ax.set_ylim(-0.05, 1.05)
    zoom_note = f" (zoom eta<= {eta_max:g})" if eta_max is not None else ""
    ax.set_title(title + zoom_note)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_time_series(series_rows, rho_label: str, metric: str, out_path: Path):
    mean_key = f"{metric}_mean"
    stdev_key = f"{metric}_stdev"
    fig, ax = plt.subplots(figsize=(7, 5))
    by_eta = defaultdict(list)
    for row in series_rows:
        if row["rho_label"] != rho_label:
            continue
        eta = float(row["eta"])
        if not any(abs(eta - target) < 1e-9 for target in SERIES_ETA_SUBSET):
            continue
        by_eta[eta].append((int(row["t"]), float(row[mean_key]), float(row[stdev_key])))

    for eta in sorted(by_eta.keys()):
        points = sorted(by_eta[eta])
        ts = [p[0] for p in points]
        means = [p[1] for p in points]
        stds = [p[2] for p in points]
        ax.plot(ts, means, marker=".", markersize=3, label=f"eta={eta:g}")
        lower = [m - s for m, s in zip(means, stds)]
        upper = [m + s for m, s in zip(means, stds)]
        ax.fill_between(ts, lower, upper, alpha=0.15)

    ax.axvline(1500, color="black", linestyle="--", linewidth=1, alpha=0.8, label="t_eq=1500")
    ax.set_xlabel("paso t")
    ax.set_ylabel(f"{metric}(t) (promedio entre realizaciones +/- 1 desvio)")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(f"Vicsek, {RHO_DISPLAY[rho_label]}: relajacion de {metric}(t)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="vicsek_lowrho_cluster_study_1")
    args = parser.parse_args()

    summary_dir = REPO_ROOT / "data" / "summary"
    by_combo_rows = read_csv_rows(summary_dir / f"{args.run_name}_by_combo.csv")
    series_rows = read_csv_rows(summary_dir / f"{args.run_name}_series_sampled.csv")

    out_dir = REPO_ROOT / "figures" / args.run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_metric_vs_eta(
        by_combo_rows, "va_mean", "va_stdev_between_realizations",
        "Vicsek, densidades bajas: polarizacion estacionaria vs ruido (R=20)",
        "<va> estacionario", out_dir / "va_vs_eta.png")
    plot_metric_vs_eta(
        by_combo_rows, "S_mean", "S_stdev_between_realizations",
        "Vicsek, densidades bajas: fraccion del cluster mas grande vs ruido (R=20)",
        "<S> estacionario", out_dir / "S_vs_eta.png")
    plot_metric_vs_eta(
        by_combo_rows, "va_mean", "va_stdev_between_realizations",
        "Vicsek, densidades bajas: polarizacion estacionaria vs ruido (R=20)",
        "<va> estacionario", out_dir / "va_vs_eta_zoom_0_1.5.png", eta_max=1.5)
    plot_metric_vs_eta(
        by_combo_rows, "S_mean", "S_stdev_between_realizations",
        "Vicsek, densidades bajas: fraccion del cluster mas grande vs ruido (R=20)",
        "<S> estacionario", out_dir / "S_vs_eta_zoom_0_1.5.png", eta_max=1.5)
    for rho_label in RHO_LABELS_ORDER:
        plot_time_series(series_rows, rho_label, "va", out_dir / f"va_t_{rho_label}.png")
        plot_time_series(series_rows, rho_label, "S", out_dir / f"S_t_{rho_label}.png")

    print(f"Graficos escritos en {out_dir.relative_to(REPO_ROOT)}/:")
    for p in sorted(out_dir.glob("*.png")):
        print(f"  {p.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
