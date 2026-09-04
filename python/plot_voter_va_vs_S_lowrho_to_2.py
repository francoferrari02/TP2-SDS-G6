#!/usr/bin/env python3
"""<va> vs. <S> para el votante, densidades desde la mas baja hasta rho=2.

Analogo a plot_vicsek_va_vs_S_lowrho_to_2.py: combina rho={1/(3pi),1/(2pi),
1/pi,2} (grilla de 37 puntos de eta cada una), leyendo las tablas finales
consolidadas:

    data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_by_combo.csv
    data/summary/final_voter_base_grid_steps3000_R20_v1_by_combo.csv (solo rho=2)

Cada punto es un eta del barrido; eta no es un eje. Color: degrade de verde,
mas claro para la densidad mas baja (rho=1/(3pi)) y mas oscuro para la mas
alta (rho=2), con marcador propio por densidad (mismos marcadores que la
version de Vicsek). Barras de error = desvio estandar entre las R=20
realizaciones (va_stdev_between_realizations, S_stdev_between_realizations).

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/plot_voter_va_vs_S_lowrho_to_2.py
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "voter_va_vs_S_lowrho_to_2_v1"

LOWRHO_RUN = "final_lowrho_cluster_grid_steps3000_R20_v1"
BASE_RUN = "final_voter_base_grid_steps3000_R20_v1"
MODEL = "voter"

RHO_ORDER = ["rho_1_over_3pi", "rho_1_over_2pi", "rho_1_over_pi", "rho_2"]
RHO_DISPLAY = {
    "rho_1_over_3pi": r"$\rho=1/(3\pi)$",
    "rho_1_over_2pi": r"$\rho=1/(2\pi)$",
    "rho_1_over_pi": r"$\rho=1/\pi$",
    "rho_2": r"$\rho=2$",
}
RHO_MARKER = {
    "rho_1_over_3pi": "v",
    "rho_1_over_2pi": "D",
    "rho_1_over_pi": "P",
    "rho_2": "o",
}
# Tonos de verde, claro (densidad baja) -> oscuro (densidad alta), muy
# espaciados entre si para que las cuatro densidades se distingan de un
# vistazo (paleta secuencial 'Greens' de ColorBrewer, extremos incluidos).
RHO_COLOR = {
    "rho_1_over_3pi": "#c7e9c0",
    "rho_1_over_2pi": "#74c476",
    "rho_1_over_pi": "#238b45",
    "rho_2": "#00441b",
}


def read_csv_rows(path: Path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def combo_curve(rows, rho_label):
    selected = [r for r in rows if r["model"] == MODEL and r["rho_label"] == rho_label]
    selected.sort(key=lambda r: float(r["eta"]))
    va_means = [float(r["va_mean"]) for r in selected]
    va_errs = [float(r["va_stdev_between_realizations"]) for r in selected]
    s_means = [float(r["S_mean"]) for r in selected]
    s_errs = [float(r["S_stdev_between_realizations"]) for r in selected]
    return va_means, va_errs, s_means, s_errs


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lowrho_rows = read_csv_rows(SUMMARY_DIR / f"{LOWRHO_RUN}_by_combo.csv")
    base_rows = read_csv_rows(SUMMARY_DIR / f"{BASE_RUN}_by_combo.csv")
    rows_by_rho = {
        "rho_1_over_3pi": lowrho_rows, "rho_1_over_2pi": lowrho_rows, "rho_1_over_pi": lowrho_rows,
        "rho_2": base_rows,
    }

    plt.rcParams.update({
        "font.size": 20,
        "axes.labelsize": 24,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 18,
        "axes.grid": False,
        "lines.markersize": 9,
        "lines.linewidth": 0.0,
        "errorbar.capsize": 3,
    })

    fig, ax = plt.subplots(figsize=(8.5, 7.4))
    for rho_label in reversed(RHO_ORDER):
        va_means, va_errs, s_means, s_errs = combo_curve(rows_by_rho[rho_label], rho_label)
        ax.errorbar(
            va_means, s_means, xerr=va_errs, yerr=s_errs,
            marker=RHO_MARKER[rho_label], linestyle="none",
            color=RHO_COLOR[rho_label], ecolor=RHO_COLOR[rho_label],
            elinewidth=1.4, capthick=1.4, markeredgecolor="none",
            label=RHO_DISPLAY[rho_label],
        )

    ax.set_xlabel(r"Polarización $v_a$")
    ax.set_ylabel(r"Componente gigante $S$")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(False)
    ax.legend(loc="lower right", frameon=False, title="Votante", title_fontsize=19)

    fig.tight_layout()
    out_path = OUT_DIR / "voter_va_vs_S_lowrho_to_2.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"Figura escrita en {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
