#!/usr/bin/env python3
"""Grafica la relacion exploratoria entre polarizacion y cluster gigante.

La figura reproduce la orientacion de ejes de la referencia externa
(x=<va>, y=<S>) y combina las seis densidades disponibles para ambos modelos.
No reemplaza la figura obligatoria del punto E, que conserva x=<S>, y=<va> y
solo rho={2,4,8} en figures/final_production_v1/.

Lee exclusivamente tablas finales ya consolidadas; no ejecuta simulaciones ni
recomputa observables.
"""

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = REPO_ROOT / "data" / "summary"
OUT_DIR = REPO_ROOT / "figures" / "cluster_order_relationship_v1"

BASE_FILES = {
    "vicsek": SUMMARY_DIR / "final_vicsek_base_grid_steps3000_R20_v1_by_combo.csv",
    "voter": SUMMARY_DIR / "final_voter_base_grid_steps3000_R20_v1_by_combo.csv",
}
LOWRHO_FILE = SUMMARY_DIR / "final_lowrho_cluster_grid_steps3000_R20_v1_by_combo.csv"

ETA_VALUES = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
RHO_ORDER = [
    "rho_8",
    "rho_4",
    "rho_2",
    "rho_1_over_pi",
    "rho_1_over_2pi",
    "rho_1_over_3pi",
]
RHO_DISPLAY = {
    "rho_8": r"$\rho=8$ (N=800)",
    "rho_4": r"$\rho=4$ (N=400)",
    "rho_2": r"$\rho=2$ (N=200)",
    "rho_1_over_pi": r"$\rho=1/\pi$ (N=32)",
    "rho_1_over_2pi": r"$\rho=1/(2\pi)$ (N=16)",
    "rho_1_over_3pi": r"$\rho=1/(3\pi)$ (N=11)",
}
RHO_COLOR = {
    "rho_8": "#2ca02c",
    "rho_4": "#d62728",
    "rho_2": "#1f77b4",
    "rho_1_over_pi": "#7b3294",
    "rho_1_over_2pi": "#e08214",
    "rho_1_over_3pi": "#01665e",
}
MODEL_DISPLAY = {"vicsek": "Vicsek", "voter": "votante"}
MODEL_MARKER = {"vicsek": "o", "voter": "x"}


def read_rows(path: Path):
    with path.open("r", newline="") as handle:
        return list(csv.DictReader(handle))


def load_rows():
    rows = []
    for model, path in BASE_FILES.items():
        rows.extend(r for r in read_rows(path) if r["model"] == model)
    rows.extend(read_rows(LOWRHO_FILE))
    return rows


def validate(rows):
    expected = {(model, rho, eta) for model in MODEL_DISPLAY for rho in RHO_ORDER for eta in ETA_VALUES}
    observed = set()
    for row in rows:
        key = (row["model"], row["rho_label"], round(float(row["eta"]), 12))
        if key in observed:
            raise ValueError(f"combinacion duplicada: {key}")
        observed.add(key)
        if int(row["realizations"]) != 20:
            raise ValueError(f"R distinto de 20 en {key}")
        for field in ("va_mean", "S_mean"):
            value = float(row[field])
            # Los agregados pueden exceder 1 por unas pocas ULP al promediar.
            if not -1e-12 <= value <= 1.0 + 1e-12:
                raise ValueError(f"{field} fuera de [0,1] en {key}: {value}")
    normalized_expected = {(m, r, round(e, 12)) for m, r, e in expected}
    if observed != normalized_expected:
        missing = sorted(normalized_expected - observed)
        extra = sorted(observed - normalized_expected)
        raise ValueError(f"matriz incompleta: faltan={missing}, sobran={extra}")


def pearson(xs, ys):
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    centered_x = [x - mean_x for x in xs]
    centered_y = [y - mean_y for y in ys]
    denominator = math.sqrt(sum(x * x for x in centered_x) * sum(y * y for y in centered_y))
    return sum(x * y for x, y in zip(centered_x, centered_y)) / denominator


def write_summary(rows):
    path = OUT_DIR / "correlation_summary.csv"
    fields = ["model", "rho_label", "pearson_va_S", "va_min", "va_max", "S_min", "S_max", "n_eta"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model in MODEL_DISPLAY:
            for rho in RHO_ORDER:
                selected = [r for r in rows if r["model"] == model and r["rho_label"] == rho]
                selected.sort(key=lambda r: float(r["eta"]))
                va = [float(r["va_mean"]) for r in selected]
                cluster = [float(r["S_mean"]) for r in selected]
                writer.writerow({
                    "model": model,
                    "rho_label": rho,
                    "pearson_va_S": f"{pearson(va, cluster):.12g}",
                    "va_min": f"{min(va):.12g}",
                    "va_max": f"{max(va):.12g}",
                    "S_min": f"{min(cluster):.12g}",
                    "S_max": f"{max(cluster):.12g}",
                    "n_eta": len(selected),
                })
    return path


def plot(rows):
    plt.rcParams.update({
        "font.size": 20,
        "axes.labelsize": 23,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "legend.fontsize": 16,
        "axes.grid": False,
    })
    fig, ax = plt.subplots(figsize=(14.2, 8.5))
    for rho in RHO_ORDER:
        for model in ("vicsek", "voter"):
            selected = [r for r in rows if r["model"] == model and r["rho_label"] == rho]
            selected.sort(key=lambda r: float(r["eta"]))
            va = [float(r["va_mean"]) for r in selected]
            cluster = [float(r["S_mean"]) for r in selected]
            marker = MODEL_MARKER[model]
            ax.plot(
                va,
                cluster,
                linestyle="none",
                marker=marker,
                markersize=8 if model == "vicsek" else 9,
                markeredgewidth=2.0 if model == "voter" else 1.0,
                color=RHO_COLOR[rho],
                alpha=0.82,
                label=f"{MODEL_DISPLAY[model]} {RHO_DISPLAY[rho]}",
            )
    ax.set_xlabel(r"polarizacion $\langle v_a\rangle$")
    ax.set_ylabel(r"fraccion del mayor cluster $\langle S\rangle$")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(0.08, 1.04)
    ax.grid(False)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, ncol=1)
    fig.tight_layout()
    path = OUT_DIR / "comparison_va_vs_S_six_densities.png"
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    validate(rows)
    figure = plot(rows)
    summary = write_summary(rows)
    print(f"Figura: {figure.relative_to(REPO_ROOT)}")
    print(f"Resumen: {summary.relative_to(REPO_ROOT)}")
    print(f"Combinaciones validadas: {len(rows)} (2 modelos x 6 densidades x 14 eta)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
