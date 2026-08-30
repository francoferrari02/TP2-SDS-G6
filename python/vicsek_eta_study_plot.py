#!/usr/bin/env python3
"""Graficos diagnosticos del barrido de eta para Vicsek.

Lee las tablas livianas generadas por `python/pilot_analyze.py` y escribe
figuras bajo `figures/<run-name>/`. No toca los observables crudos.
Requiere matplotlib.

Uso:
    python3 python/vicsek_eta_study_plot.py \
        --run-name vicsek_eta0_6_deta0p5_steps3000_R20_v1
"""

import argparse
import csv
import os
import tempfile
from collections import defaultdict
from pathlib import Path

_MPL_CACHE = Path(tempfile.gettempdir()) / "tp2_matplotlib_cache"
_MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parent.parent

RHO_LABELS_ORDER = ["rho_2", "rho_4", "rho_8"]
RHO_DISPLAY = {"rho_2": "rho=2", "rho_4": "rho=4", "rho_8": "rho=8"}
RHO_COLORS = {"rho_2": "#1f77b4", "rho_4": "#d62728", "rho_8": "#2ca02c"}
SERIES_ETA_SUBSET = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

plt.rcParams.update({
    "font.size": 12,
    "axes.labelsize": 13,
    "axes.titlesize": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
})


def read_csv_rows(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"No existe {path.relative_to(REPO_ROOT)}")
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def eta_value(row):
    return float(row["eta"])


def rows_for_rho(rows, rho_label: str, eta_max=None):
    return sorted(
        (
            row for row in rows
            if row["rho_label"] == rho_label
            and (eta_max is None or eta_value(row) <= eta_max)
        ),
        key=eta_value,
    )


def save_metric_vs_eta(by_combo_rows, out_path: Path, metric: str, eta_max=None):
    metric_config = {
        "va": {
            "mean": "va_mean",
            "err": "va_stderr",
            "ylabel": r"$\langle v_a \rangle$ estacionario",
            "title": "Vicsek: polarizacion estacionaria vs ruido",
        },
        "S": {
            "mean": "S_mean",
            "err": "S_stderr",
            "ylabel": r"$\langle S \rangle$ estacionario",
            "title": "Vicsek: componente gigante vs ruido",
        },
    }
    cfg = metric_config[metric]

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for rho_label in RHO_LABELS_ORDER:
        rows = rows_for_rho(by_combo_rows, rho_label, eta_max=eta_max)
        if not rows:
            continue
        etas = [eta_value(row) for row in rows]
        means = [float(row[cfg["mean"]]) for row in rows]
        errors = [float(row[cfg["err"]]) for row in rows]
        ax.errorbar(
            etas,
            means,
            yerr=errors,
            marker="o",
            linewidth=1.6,
            markersize=4,
            capsize=3,
            color=RHO_COLORS[rho_label],
            label=RHO_DISPLAY[rho_label],
        )

    ax.set_xlabel(r"$\eta$")
    ax.set_ylabel(cfg["ylabel"])
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(left=-0.05)
    title_suffix = f" (zoom $\\eta \\leq {eta_max:g}$)" if eta_max is not None else ""
    ax.set_title(f"{cfg['title']}{title_suffix}\nR=20, barras = error estandar")
    ax.legend(frameon=False)
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_va_vs_s(by_combo_rows, out_path: Path):
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for rho_label in RHO_LABELS_ORDER:
        rows = rows_for_rho(by_combo_rows, rho_label)
        if not rows:
            continue
        s_mean = [float(row["S_mean"]) for row in rows]
        va_mean = [float(row["va_mean"]) for row in rows]
        s_err = [float(row["S_stderr"]) for row in rows]
        va_err = [float(row["va_stderr"]) for row in rows]
        ax.errorbar(
            s_mean,
            va_mean,
            xerr=s_err,
            yerr=va_err,
            marker="o",
            linewidth=1.3,
            markersize=4,
            capsize=3,
            color=RHO_COLORS[rho_label],
            label=RHO_DISPLAY[rho_label],
        )

    ax.set_xlabel(r"$\langle S \rangle$ estacionario")
    ax.set_ylabel(r"$\langle v_a \rangle$ estacionario")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Vicsek: relacion entre orden y conectividad\nR=20, barras = error estandar")
    ax.legend(frameon=False)
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def grouped_time_series(series_rows, rho_label: str, metric: str):
    mean_key = f"{metric}_mean"
    band_key = f"{metric}_stderr"
    band_label = "error estandar"
    if series_rows and band_key not in series_rows[0]:
        band_key = f"{metric}_stdev"
        band_label = "desvio entre realizaciones"
    if not series_rows or mean_key not in series_rows[0] or band_key not in series_rows[0]:
        return {}, band_label

    by_eta = defaultdict(list)
    for row in series_rows:
        if row["rho_label"] != rho_label:
            continue
        eta = float(row["eta"])
        if not any(abs(eta - target) < 1e-9 for target in SERIES_ETA_SUBSET):
            continue
        by_eta[eta].append((int(row["t"]), float(row[mean_key]), float(row[band_key])))
    return by_eta, band_label


def save_time_series(series_rows, rho_label: str, metric: str, out_path: Path, t_eq: int):
    metric_config = {
        "va": {
            "ylabel": r"$v_a(t)$ promedio entre realizaciones",
            "title": f"Vicsek, {RHO_DISPLAY[rho_label]}: relajacion de polarizacion",
        },
        "S": {
            "ylabel": r"$S(t)$ promedio entre realizaciones",
            "title": f"Vicsek, {RHO_DISPLAY[rho_label]}: relajacion de componente gigante",
        },
    }
    by_eta, band_label = grouped_time_series(series_rows, rho_label, metric)
    if not by_eta:
        return False

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for eta in sorted(by_eta.keys()):
        points = sorted(by_eta[eta])
        ts = [point[0] for point in points]
        means = [point[1] for point in points]
        stds = [point[2] for point in points]
        lower = [max(0.0, mean - std) for mean, std in zip(means, stds)]
        upper = [min(1.0, mean + std) for mean, std in zip(means, stds)]
        ax.plot(ts, means, linewidth=1.4, marker=".", markersize=3, label=fr"$\eta={eta:g}$")
        ax.fill_between(ts, lower, upper, alpha=0.12)

    ax.axvline(t_eq, color="0.25", linestyle="--", linewidth=1.2, label=fr"$t_{{eq}}={t_eq}$")
    ax.set_xlabel("paso t")
    ax.set_ylabel(metric_config[metric]["ylabel"])
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(f"{metric_config[metric]['title']}\nR=20, banda = {band_label}")
    ax.legend(frameon=False, ncol=2)
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="vicsek_eta0_6_deta0p5_steps3000_R20_v1")
    parser.add_argument("--t-eq", type=int, default=1500,
                        help="paso donde empieza la ventana estacionaria graficada")
    args = parser.parse_args()

    summary_dir = REPO_ROOT / "data" / "summary"
    by_combo_rows = read_csv_rows(summary_dir / f"{args.run_name}_by_combo.csv")
    series_rows = read_csv_rows(summary_dir / f"{args.run_name}_series_sampled.csv")

    out_dir = REPO_ROOT / "figures" / args.run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    targets = [
        ("va_vs_eta.png", lambda p: save_metric_vs_eta(by_combo_rows, p, "va")),
        ("S_vs_eta.png", lambda p: save_metric_vs_eta(by_combo_rows, p, "S")),
        ("va_vs_eta_zoom_0_1.5.png", lambda p: save_metric_vs_eta(by_combo_rows, p, "va", eta_max=1.5)),
        ("S_vs_eta_zoom_0_1.5.png", lambda p: save_metric_vs_eta(by_combo_rows, p, "S", eta_max=1.5)),
        ("va_vs_S.png", lambda p: save_va_vs_s(by_combo_rows, p)),
    ]
    for filename, writer in targets:
        out_path = out_dir / filename
        writer(out_path)
        written.append(out_path)

    skipped_s = False
    for rho_label in RHO_LABELS_ORDER:
        va_path = out_dir / f"va_t_{rho_label}.png"
        if save_time_series(series_rows, rho_label, "va", va_path, args.t_eq):
            written.append(va_path)

        s_path = out_dir / f"S_t_{rho_label}.png"
        if save_time_series(series_rows, rho_label, "S", s_path, args.t_eq):
            written.append(s_path)
        else:
            skipped_s = True

    print(f"Graficos escritos en {out_dir.relative_to(REPO_ROOT)}/:")
    for path in sorted(written):
        print(f"  {path.name}")
    if skipped_s:
        print("\nAviso: no se generaron S_t_*.png porque la tabla *_series_sampled.csv no tiene S_mean/S_stderr.")
        print("Regenere el resumen con: python3 python/pilot_analyze.py --run-name <run-name> --sample-stride 50")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
