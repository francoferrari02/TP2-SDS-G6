#!/usr/bin/env python3
"""Grafico del benchmark TP1 vs TP2 (etapa 8).

Lee data/summary/benchmark_tp1_vs_tp2.csv (generado por
benchmark_tp1_vs_tp2.py) y produce dos paneles:
  - izquierda: tiempo de busqueda de vecinos vs N, escala log-log, las tres
    condiciones con barras de desvio estandar (de las 100 repeticiones).
  - derecha: numero medio de vecinos por particula vs N, para mostrar que
    la condicion "radio" (TP1 real) encuentra sistematicamente mas vecinos
    que las dos condiciones puntuales (TP1 ablacionado y TP2), pese a usar
    el mismo rc nominal -- es una de las causas de su tiempo mayor.

Uso:
    python3 python/benchmark_tp1_vs_tp2_plot.py
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent

LABELS = {
    "tp1_radio": "TP1 real (radio, no superposición, M=13)",
    "tp1_puntual": "TP1 puntual (ablación, M=20)",
    "tp2": "TP2 (C++, puntual, M=20)",
}
COLORS = {"tp1_radio": "#d62728", "tp1_puntual": "#e08214", "tp2": "#1f77b4"}
MARKERS = {"tp1_radio": "o", "tp1_puntual": "s", "tp2": "^"}


def main() -> int:
    path = REPO_ROOT / "data" / "summary" / "benchmark_tp1_vs_tp2.csv"
    data = defaultdict(list)
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            data[row["condicion"]].append({
                "N": int(row["N"]),
                "M": int(row["M"]),
                "mean": float(row["tiempo_promedio_s"]) * 1000.0,  # a ms
                "std": float(row["tiempo_std_s"]) * 1000.0,
                "mean_k": float(row["mean_k"]),
            })

    fig, (ax_t, ax_k) = plt.subplots(1, 2, figsize=(13, 5.5))

    for cond in ["tp1_radio", "tp1_puntual", "tp2"]:
        rows = sorted(data[cond], key=lambda r: r["N"])
        ns = [r["N"] for r in rows]
        means = [r["mean"] for r in rows]
        stds = [r["std"] for r in rows]
        ax_t.errorbar(ns, means, yerr=stds, marker=MARKERS[cond], capsize=3,
                       color=COLORS[cond], label=LABELS[cond])

        mean_ks = [r["mean_k"] for r in rows]
        ax_k.plot(ns, mean_ks, marker=MARKERS[cond], color=COLORS[cond], label=LABELS[cond])

    ax_t.set_xscale("log")
    ax_t.set_yscale("log")
    ax_t.set_xlabel("N (partículas)")
    ax_t.set_ylabel("Tiempo de búsqueda de vecinos (ms)")
    ax_t.set_title("CIM: tiempo vs N (L=20, rc=1, periódico, R=100 repeticiones)")
    ax_t.legend(fontsize=9)
    ax_t.grid(True, which="both", alpha=0.25)

    ax_k.set_xscale("log")
    ax_k.set_xlabel("N (partículas)")
    ax_k.set_ylabel("Vecinos medios por partícula")
    ax_k.set_title("Vecinos medios encontrados (misma rc nominal)")
    ax_k.legend(fontsize=9)
    ax_k.grid(True, which="both", alpha=0.25)

    fig.tight_layout()
    out_dir = REPO_ROOT / "figures" / "benchmark_tp1_vs_tp2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tiempo_y_vecinos_vs_N.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"Escrito: {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
