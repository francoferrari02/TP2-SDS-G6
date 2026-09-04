# Fotogramas votante rho=2, eta=0.1 y eta=1

Figura estatica lado a lado generada desde `trajectory.csv`, sin ejecutar simulacion dentro del renderizador.

## Protocolo

- Modelo: votante.
- Densidad: `rho=2`, `N=200`, `L=10`.
- Tiempo mostrado: `t=2000` (`t_eq=1500`, ventana estacionaria).
- Corridas: `steps=3000`, `trajectory_stride=10`, `observables_stride=100`.
- Panel izquierdo: `eta=0.1`, `base_seed=940000`, realizacion `0`.
- Panel derecho: `eta=1`, `base_seed=950000`, realizacion `0`.
- Color: angulo `theta` en radianes, mapa ciclico HSV.
- Longitud: rapidez fisica constante `v=0.03` amplificada por factor comun `15.0` solo por legibilidad.

## Archivos

- PNG: `figures/voter_rho2_eta0p5_eta1_snapshots_v1/voter_rho2_eta0p5_eta1_t2000_side_by_side.png`
- Script: `python/render_voter_rho2_eta0p5_eta1_snapshots.py`

## Evidencia

- `eta=0.1`: `N=200`, `va(t=2000)=0.972763`, `trajectory=data/illustrations/voter_rho2_eta0p5_eta1_snapshots_v1/voter/rho_2/eta_0p10000000000000001/steps_3000/realization_000_seed_940000/trajectory.csv`.
- `eta=1`: `N=200`, `va(t=2000)=0.353513`, `trajectory=data/illustrations/voter_rho2_eta0p5_eta1_snapshots_v1/voter/rho_2/eta_1/steps_3000/realization_000_seed_950000/trajectory.csv`.
