# Fotogramas Vicsek rho=2, eta=1 y eta=5

Figura estatica lado a lado generada desde `trajectory.csv`, sin ejecutar simulacion dentro del renderizador.

## Protocolo

- Modelo: Vicsek.
- Densidad: `rho=2`, `N=200`, `L=10`.
- Tiempo mostrado: `t=2000` (`t_eq=1500`, ventana estacionaria).
- Corridas: `steps=3000`, `trajectory_stride=10`, `observables_stride=100`.
- Panel izquierdo: `eta=1`, `base_seed=922000`, realizacion `0`.
- Panel derecho: `eta=5`, `base_seed=930000`, realizacion `0`.
- Color: angulo `theta` en radianes, mapa ciclico HSV.
- Longitud: rapidez fisica constante `v=0.03` amplificada por factor comun `15.0` solo por legibilidad.

## Archivos

- PNG: `figures/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek_rho2_eta1_eta5_t2000_side_by_side.png`
- Script: `python/render_vicsek_rho2_eta1_eta5_snapshots.py`

## Evidencia

- `eta=1`: `N=200`, `va(t=2000)=0.927548`, `trajectory=data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek/rho_2/eta_1/steps_3000/realization_000_seed_922000/trajectory.csv`.
- `eta=5`: `N=200`, `va(t=2000)=0.088270`, `trajectory=data/illustrations/vicsek_rho2_eta1_eta5_snapshots_v1/vicsek/rho_2/eta_5/steps_3000/realization_000_seed_930000/trajectory.csv`.
