#!/usr/bin/env python3
"""Animacion MP4 Vicsek rho=2, eta=1 vs eta=5, con va(t)/S(t) en vivo.

Usa los mismos casos/semillas que render_vicsek_rho2_eta1_eta5_snapshots.py
(fotograma estatico en t=2000), pero la trayectoria completa (steps=3000,
trajectory_stride=10, observables_stride=10, regenerada para esta tarea).

Uso:
    python3 python/render_vicsek_rho2_eta1_eta5_animation.py
"""

from pathlib import Path

from render_comparison_animation import render

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / "data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek/rho_2"

CASES = [
    {
        "label": r"$\eta=1$",
        "trajectory": BASE / "eta_1/steps_3000/realization_000_seed_922000/trajectory.csv",
        "observables": BASE / "eta_1/steps_3000/realization_000_seed_922000/observables.csv",
    },
    {
        "label": r"$\eta=5$",
        "trajectory": BASE / "eta_5/steps_3000/realization_000_seed_930000/trajectory.csv",
        "observables": BASE / "eta_5/steps_3000/realization_000_seed_930000/observables.csv",
    },
]

OUT_PATH = REPO_ROOT / "figures/animations_v1/vicsek_rho2_eta1_eta5.mp4"

if __name__ == "__main__":
    render(CASES, OUT_PATH)
