#!/usr/bin/env python3
"""Animacion MP4 votante rho=2, eta=0.1 vs eta=1, con va(t)/S(t) en vivo.

Usa los mismos casos/semillas que render_voter_rho2_eta0p5_eta1_snapshots.py
(fotograma estatico en t=2000), pero la trayectoria completa (steps=3000,
trajectory_stride=10, observables_stride=10, regenerada para esta tarea).

Uso:
    python3 python/render_voter_rho2_eta0p1_eta1_animation.py
"""

from pathlib import Path

from render_comparison_animation import render

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / "data/illustrations/voter_rho2_eta0p5_eta1_snapshots_v1/voter/rho_2"

CASES = [
    {
        "label": r"$\eta=0.1$",
        "trajectory": BASE / "eta_0p10000000000000001/steps_3000/realization_000_seed_940000/trajectory.csv",
        "observables": BASE / "eta_0p10000000000000001/steps_3000/realization_000_seed_940000/observables.csv",
    },
    {
        "label": r"$\eta=1$",
        "trajectory": BASE / "eta_1/steps_3000/realization_000_seed_950000/trajectory.csv",
        "observables": BASE / "eta_1/steps_3000/realization_000_seed_950000/observables.csv",
    },
]

OUT_PATH = REPO_ROOT / "figures/animations_v1/voter_rho2_eta0p1_eta1.mp4"

if __name__ == "__main__":
    render(CASES, OUT_PATH)
