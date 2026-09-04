#!/usr/bin/env python3
"""Lanza las 4 animaciones individuales (2 Vicsek, 2 votante), rho=2.

Usa las mismas semillas/trayectorias ya generadas para las figuras
comparativas (render_vicsek_rho2_eta1_eta5_snapshots.py,
render_voter_rho2_eta0p5_eta1_snapshots.py), con observables_stride=10
(igual que trajectory_stride) para que va(t)/S(t) tengan un valor exacto en
cada fotograma.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/render_all_single_case_animations.py
"""

from pathlib import Path

from render_single_case_animation import render

REPO_ROOT = Path(__file__).resolve().parent.parent
VICSEK_BASE = REPO_ROOT / "data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek/rho_2"
VOTER_BASE = REPO_ROOT / "data/illustrations/voter_rho2_eta0p5_eta1_snapshots_v1/voter/rho_2"
OUT_DIR = REPO_ROOT / "figures" / "animations_v1"

CASES = [
    {
        "name": "vicsek_rho2_eta1",
        "label": r"Vicsek, $\eta=1$",
        "trajectory": VICSEK_BASE / "eta_1/steps_3000/realization_000_seed_922000/trajectory.csv",
        "observables": VICSEK_BASE / "eta_1/steps_3000/realization_000_seed_922000/observables.csv",
    },
    {
        "name": "vicsek_rho2_eta5",
        "label": r"Vicsek, $\eta=5$",
        "trajectory": VICSEK_BASE / "eta_5/steps_3000/realization_000_seed_930000/trajectory.csv",
        "observables": VICSEK_BASE / "eta_5/steps_3000/realization_000_seed_930000/observables.csv",
    },
    {
        "name": "voter_rho2_eta0p1",
        "label": r"Votante, $\eta=0.1$",
        "trajectory": VOTER_BASE / "eta_0p10000000000000001/steps_3000/realization_000_seed_940000/trajectory.csv",
        "observables": VOTER_BASE / "eta_0p10000000000000001/steps_3000/realization_000_seed_940000/observables.csv",
    },
    {
        "name": "voter_rho2_eta1",
        "label": r"Votante, $\eta=1$",
        "trajectory": VOTER_BASE / "eta_1/steps_3000/realization_000_seed_950000/trajectory.csv",
        "observables": VOTER_BASE / "eta_1/steps_3000/realization_000_seed_950000/observables.csv",
    },
]

if __name__ == "__main__":
    for case in CASES:
        render(case["label"], case["trajectory"], case["observables"],
               OUT_DIR / f"{case['name']}.mp4")
