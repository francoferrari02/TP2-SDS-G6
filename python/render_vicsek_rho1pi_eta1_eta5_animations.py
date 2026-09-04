#!/usr/bin/env python3
"""Animaciones individuales Vicsek rho=1/pi (N=32), eta=1 y eta=5.

Contraste con vicsek_rho2_eta1 / vicsek_rho2_eta5: en esta densidad baja
(separacion media entre particulas mucho mayor que rc=1) S(t) si depende
fuertemente del ruido, a diferencia de rho=2 donde S~1 casi siempre por
pura conectividad geometrica.

Uso:
    MPLCONFIGDIR=/private/tmp/tp2_mplconfig .venv-mpl311/bin/python \
        python/render_vicsek_rho1pi_eta1_eta5_animations.py
"""

from pathlib import Path

from render_single_case_animation import render

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / "data/illustrations/vicsek_rho1pi_eta1_eta5_snapshots_v1/vicsek/rho_1_over_pi"
OUT_DIR = REPO_ROOT / "figures" / "animations_v1"

CASES = [
    {
        "name": "vicsek_rho1pi_eta1",
        "label": r"Vicsek, $\rho=1/\pi$, $\eta=1$",
        "trajectory": BASE / "eta_1/steps_3000/realization_000_seed_960000/trajectory.csv",
        "observables": BASE / "eta_1/steps_3000/realization_000_seed_960000/observables.csv",
    },
    {
        "name": "vicsek_rho1pi_eta5",
        "label": r"Vicsek, $\rho=1/\pi$, $\eta=5$",
        "trajectory": BASE / "eta_5/steps_3000/realization_000_seed_970000/trajectory.csv",
        "observables": BASE / "eta_5/steps_3000/realization_000_seed_970000/observables.csv",
    },
]

if __name__ == "__main__":
    for case in CASES:
        render(case["label"], case["trajectory"], case["observables"],
               OUT_DIR / f"{case['name']}.mp4")
