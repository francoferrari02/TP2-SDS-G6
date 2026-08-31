#!/usr/bin/env python3
"""Genera todas las figuras finales del TP2 en figures/final_production_v1/.

Lee exclusivamente las tres tablas consolidadas finales:

    data/summary/final_vicsek_base_grid_steps3000_R20_v1_*.csv
    data/summary/final_voter_base_grid_steps3000_R20_v1_*.csv
    data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_*.csv

No ejecuta simulaciones, no recomputa observables y no escribe fuera de
figures/final_production_v1/.

Protocolo vinculante de las figuras (ver plan_desarrollo_tp2/06 y 07):

    eta = {0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1, 2, 3, 4, 5, 6}
    steps = 3000, R = 20, t_eq = 1500, ventana estacionaria t=1500..3000
    barras estacionarias = desvio estandar entre realizaciones
                           (va_stdev_between_realizations / S_stdev_between_realizations)
    bandas en series temporales = desvio estandar entre realizaciones por instante
                           (va_stdev / S_stdev)

Convenciones de presentacion:

    - sin titulo interno ni caption dentro de la figura;
    - sin grilla de fondo;
    - va y S en figuras separadas, con eje y en [0,1] salvo margen visual minimo;
    - color por densidad, constante en todas las figuras;
    - modelo distinguido por marcador y estilo de linea;
    - puntos visibles; las lineas solo conectan puntos como guia visual;
    - fuente >= 20 pt; PNG a 220 dpi.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/generate_final_figures.py
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
DEFAULT_OUT_DIR = REPO_ROOT / "figures" / "final_production_v1"

VICSEK_RUN = "final_vicsek_base_grid_steps3000_R20_v1"
VOTER_RUN = "final_voter_base_grid_steps3000_R20_v1"
LOWRHO_RUN = "final_lowrho_cluster_grid_steps3000_R20_v1"

T_EQ = 1500
DPI = 220
ZOOM_ETA_MAX = 0.5

BASE_RHO_ORDER = ["rho_2", "rho_4", "rho_8"]
LOW_RHO_ORDER = ["rho_1_over_pi", "rho_1_over_2pi", "rho_1_over_3pi"]

# Color por densidad, identico en todas las figuras de este directorio.
RHO_COLOR = {
    "rho_2": "#1f77b4",
    "rho_4": "#d62728",
    "rho_8": "#2ca02c",
    "rho_1_over_pi": "#7b3294",
    "rho_1_over_2pi": "#e08214",
    "rho_1_over_3pi": "#01665e",
}
RHO_DISPLAY = {
    "rho_2": r"$\rho=2$ (N=200)",
    "rho_4": r"$\rho=4$ (N=400)",
    "rho_8": r"$\rho=8$ (N=800)",
    "rho_1_over_pi": r"$\rho=1/\pi$ (N=32)",
    "rho_1_over_2pi": r"$\rho=1/(2\pi)$ (N=16)",
    "rho_1_over_3pi": r"$\rho=1/(3\pi)$ (N=11)",
}

MODEL_DISPLAY = {"vicsek": "Vicsek", "voter": "votante"}
MODEL_MARKER = {"vicsek": "o", "voter": "s"}
MODEL_LINESTYLE = {"vicsek": "-", "voter": "--"}

# Casos de ruido bajo y alto usados en las series temporales.
SERIES_ETAS = [0.0, 0.40, 6.0]
SERIES_ETA_COLOR = {0.0: "#08519c", 0.40: "#e6550d", 6.0: "#31a354"}

Y_LIMITS = (-0.04, 1.04)

AXIS_LABEL = {
    "va_eta": r"ruido $\eta$ [rad]",
    "va_mean": r"polarización $\langle v_a\rangle$",
    "S_mean": r"fracción del mayor cluster $\langle S\rangle$",
    "t": "tiempo t [pasos]",
    "va_t": r"polarización $v_a(t)$",
    "S_t": r"fracción del mayor cluster $S(t)$",
}


def apply_style() -> None:
    plt.rcParams.update({
        "font.size": 21,
        "axes.labelsize": 23,
        "axes.titlesize": 23,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 19,
        "axes.grid": False,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "lines.markersize": 8,
        "lines.linewidth": 2.0,
        "errorbar.capsize": 4,
    })


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def load_tables():
    tables = {}
    for key, run in (("vicsek", VICSEK_RUN), ("voter", VOTER_RUN), ("lowrho", LOWRHO_RUN)):
        tables[key] = {
            "by_combo": read_csv_rows(SUMMARY_DIR / f"{run}_by_combo.csv"),
            "series": read_csv_rows(SUMMARY_DIR / f"{run}_series_sampled.csv"),
        }
    return tables


def save(fig, out_dir: Path, name: str, generated: list) -> None:
    path = out_dir / name
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    generated.append(name)
    print(f"  {name}")


def combo_curve(rows, model, rho_label, metric, eta_max=None):
    """Devuelve (etas, medias, desvios entre realizaciones) ordenados por eta."""
    selected = [r for r in rows
                if r["model"] == model and r["rho_label"] == rho_label
                and (eta_max is None or float(r["eta"]) <= eta_max + 1e-9)]
    selected.sort(key=lambda r: float(r["eta"]))
    etas = [float(r["eta"]) for r in selected]
    means = [float(r[f"{metric}_mean"]) for r in selected]
    errs = [float(r[f"{metric}_stdev_between_realizations"]) for r in selected]
    return etas, means, errs


def plot_metric_vs_eta(rows, model, rho_order, metric, out_dir, name, generated, eta_max=None):
    """Una curva por densidad, un modelo. Barras = desvio entre realizaciones."""
    fig, ax = plt.subplots(figsize=(10.0, 7.2))
    for rho_label in rho_order:
        etas, means, errs = combo_curve(rows, model, rho_label, metric, eta_max)
        ax.errorbar(etas, means, yerr=errs,
                    marker="o", linestyle="-", color=RHO_COLOR[rho_label],
                    label=RHO_DISPLAY[rho_label])
    ax.set_xlabel(AXIS_LABEL["va_eta"])
    ax.set_ylabel(AXIS_LABEL[f"{metric}_mean"])
    ax.set_ylim(*Y_LIMITS)
    if eta_max is not None:
        ax.set_xlim(-0.02, eta_max + 0.02)
    ax.grid(False)
    ax.legend(loc="best", frameon=False)
    save(fig, out_dir, name, generated)


def plot_va_vs_S(rows, model, rho_order, out_dir, name, generated):
    """x=<S>, y=<va>. Cada punto es un eta del barrido; eta no es un eje.

    La linea recorre los puntos en el orden del barrido de eta (que es el
    camino que efectivamente sigue el sistema), no en orden de S: es solo
    una guia visual entre puntos consecutivos del barrido.
    """
    fig, ax = plt.subplots(figsize=(10.0, 7.2))
    for rho_label in rho_order:
        _, s_means, s_errs = combo_curve(rows, model, rho_label, "S")
        _, va_means, va_errs = combo_curve(rows, model, rho_label, "va")
        ax.errorbar(s_means, va_means, xerr=s_errs, yerr=va_errs,
                    marker="o", linestyle="-", color=RHO_COLOR[rho_label],
                    label=RHO_DISPLAY[rho_label])
    ax.set_xlabel(AXIS_LABEL["S_mean"])
    ax.set_ylabel(AXIS_LABEL["va_mean"])
    ax.set_xlim(*Y_LIMITS)
    ax.set_ylim(*Y_LIMITS)
    ax.grid(False)
    ax.legend(loc="best", frameon=False)
    save(fig, out_dir, name, generated)


def plot_time_series(series_rows, model, rho_label, metric, out_dir, name, generated):
    """Series de ruido bajo y alto con banda = desvio entre realizaciones."""
    fig, ax = plt.subplots(figsize=(10.0, 7.2))
    by_eta = defaultdict(list)
    for r in series_rows:
        if r["model"] != model or r["rho_label"] != rho_label:
            continue
        eta = float(r["eta"])
        for target in SERIES_ETAS:
            if abs(eta - target) < 1e-6:
                by_eta[target].append(r)
    for eta in SERIES_ETAS:
        rows = sorted(by_eta[eta], key=lambda r: int(r["t"]))
        if not rows:
            continue
        ts = [int(r["t"]) for r in rows]
        means = [float(r[f"{metric}_mean"]) for r in rows]
        stdev = [float(r[f"{metric}_stdev"]) for r in rows]
        color = SERIES_ETA_COLOR[eta]
        ax.plot(ts, means, color=color, linestyle="-", label=rf"$\eta={eta:g}$")
        ax.fill_between(ts,
                        [m - s for m, s in zip(means, stdev)],
                        [m + s for m, s in zip(means, stdev)],
                        color=color, alpha=0.20, linewidth=0)
    ax.axvline(T_EQ, color="black", linestyle=":", linewidth=2.0,
               label=rf"$t_{{eq}}={T_EQ}$")
    ax.set_xlabel(AXIS_LABEL["t"])
    ax.set_ylabel(AXIS_LABEL[f"{metric}_t"])
    ax.set_ylim(*Y_LIMITS)
    ax.grid(False)
    ax.legend(loc="best", frameon=False, ncol=2)
    save(fig, out_dir, name, generated)


def plot_comparison_vs_eta(rows, rho_order, metric, out_dir, name, generated, eta_max=None):
    """Un panel por densidad; en cada panel Vicsek y votante bajo el mismo protocolo."""
    fig, axes = plt.subplots(1, len(rho_order), figsize=(9.0 * len(rho_order) / 1.6, 7.2),
                             sharey=True)
    for ax, rho_label in zip(axes, rho_order):
        for model in ("vicsek", "voter"):
            etas, means, errs = combo_curve(rows, model, rho_label, metric, eta_max)
            ax.errorbar(etas, means, yerr=errs,
                        marker=MODEL_MARKER[model], linestyle=MODEL_LINESTYLE[model],
                        color=RHO_COLOR[rho_label],
                        markerfacecolor=("none" if model == "voter" else RHO_COLOR[rho_label]),
                        label=MODEL_DISPLAY[model])
        ax.set_xlabel(AXIS_LABEL["va_eta"])
        ax.set_ylim(*Y_LIMITS)
        if eta_max is not None:
            ax.set_xlim(-0.02, eta_max + 0.02)
        ax.grid(False)
        ax.legend(loc="best", frameon=False, title=RHO_DISPLAY[rho_label],
                  title_fontsize=19)
    axes[0].set_ylabel(AXIS_LABEL[f"{metric}_mean"])
    save(fig, out_dir, name, generated)


def plot_comparison_va_vs_S(rows, rho_order, out_dir, name, generated):
    fig, axes = plt.subplots(1, len(rho_order), figsize=(9.0 * len(rho_order) / 1.6, 7.2),
                             sharey=True)
    for ax, rho_label in zip(axes, rho_order):
        for model in ("vicsek", "voter"):
            _, s_means, s_errs = combo_curve(rows, model, rho_label, "S")
            _, va_means, va_errs = combo_curve(rows, model, rho_label, "va")
            ax.errorbar(s_means, va_means, xerr=s_errs, yerr=va_errs,
                        marker=MODEL_MARKER[model], linestyle=MODEL_LINESTYLE[model],
                        color=RHO_COLOR[rho_label],
                        markerfacecolor=("none" if model == "voter" else RHO_COLOR[rho_label]),
                        label=MODEL_DISPLAY[model])
        ax.set_xlabel(AXIS_LABEL["S_mean"])
        ax.set_xlim(*Y_LIMITS)
        ax.set_ylim(*Y_LIMITS)
        ax.grid(False)
        ax.legend(loc="best", frameon=False, title=RHO_DISPLAY[rho_label],
                  title_fontsize=19)
    axes[0].set_ylabel(AXIS_LABEL["va_mean"])
    save(fig, out_dir, name, generated)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR,
                        help="directorio de salida (por defecto figures/final_production_v1)")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    figures_root = (REPO_ROOT / "figures").resolve()
    if figures_root not in out_dir.parents:
        raise SystemExit(f"--out-dir debe estar dentro de {figures_root}, recibi {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    apply_style()
    tables = load_tables()
    generated: list = []

    base = {
        "vicsek": tables["vicsek"],
        "voter": tables["voter"],
    }
    base_combo_all = tables["vicsek"]["by_combo"] + tables["voter"]["by_combo"]
    low_combo = tables["lowrho"]["by_combo"]
    low_series = tables["lowrho"]["series"]

    print(f"Escribiendo figuras en {out_dir.relative_to(REPO_ROOT)}:")

    # 1-2. Curvas estacionarias por modelo (puntos C, D y E del enunciado).
    for model in ("vicsek", "voter"):
        combo = base[model]["by_combo"]
        plot_metric_vs_eta(combo, model, BASE_RHO_ORDER, "va", out_dir,
                           f"{model}_va_vs_eta.png", generated)
        plot_metric_vs_eta(combo, model, BASE_RHO_ORDER, "va", out_dir,
                           f"{model}_va_vs_eta_zoom_0_0p5.png", generated, eta_max=ZOOM_ETA_MAX)
        plot_metric_vs_eta(combo, model, BASE_RHO_ORDER, "S", out_dir,
                           f"{model}_S_vs_eta.png", generated)
        plot_metric_vs_eta(combo, model, BASE_RHO_ORDER, "S", out_dir,
                           f"{model}_S_vs_eta_zoom_0_0p5.png", generated, eta_max=ZOOM_ETA_MAX)
        plot_va_vs_S(combo, model, BASE_RHO_ORDER, out_dir, f"{model}_va_vs_S.png", generated)

    # 3. Series temporales de la matriz base (puntos B y D).
    for model in ("vicsek", "voter"):
        series = base[model]["series"]
        for rho_label in BASE_RHO_ORDER:
            for metric in ("va", "S"):
                plot_time_series(series, model, rho_label, metric, out_dir,
                                 f"{model}_{metric}_t_{rho_label}.png", generated)

    # 4. Clusters en densidades bajas (extension del punto D).
    for model in ("vicsek", "voter"):
        plot_metric_vs_eta(low_combo, model, LOW_RHO_ORDER, "S", out_dir,
                           f"{model}_S_vs_eta_lowrho.png", generated)
        plot_metric_vs_eta(low_combo, model, LOW_RHO_ORDER, "S", out_dir,
                           f"{model}_S_vs_eta_lowrho_zoom_0_0p5.png", generated,
                           eta_max=ZOOM_ETA_MAX)
        for rho_label in LOW_RHO_ORDER:
            plot_time_series(low_series, model, rho_label, "S", out_dir,
                             f"{model}_S_t_{rho_label}_lowrho.png", generated)

    # 5. Comparacion entre modelos (punto F).
    plot_comparison_vs_eta(base_combo_all, BASE_RHO_ORDER, "va", out_dir,
                           "comparison_va_vs_eta.png", generated)
    plot_comparison_vs_eta(base_combo_all, BASE_RHO_ORDER, "S", out_dir,
                           "comparison_S_vs_eta_base.png", generated)
    plot_comparison_va_vs_S(base_combo_all, BASE_RHO_ORDER, out_dir,
                            "comparison_va_vs_S.png", generated)
    plot_comparison_vs_eta(low_combo, LOW_RHO_ORDER, "S", out_dir,
                           "comparison_S_vs_eta_lowrho.png", generated)

    print(f"\n{len(generated)} PNG generados en {out_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
