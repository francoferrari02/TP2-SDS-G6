# Relación exploratoria entre polarización y componente gigante

`comparison_va_vs_S_six_densities.png` reproduce con nuestros datos la
orientación de ejes de la figura de referencia externa:

```text
x = <va> estacionaria
y = <S> estacionaria
cada punto = un valor de eta
color = densidad
marcador = modelo (circulo: Vicsek; cruz: votante)
```

La figura muestra solamente los promedios, sin barras de desvío, para mantener
legible la superposición de doce series. El protocolo común es `steps=3000`,
`t_eq=1500`, ventana `t=1500..3000`, `R=20` y
`eta={0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,1,2,3,4,5,6}`.

Fuentes:

- `data/summary/final_vicsek_base_grid_steps3000_R20_v1_by_combo.csv`
- `data/summary/final_voter_base_grid_steps3000_R20_v1_by_combo.csv`
- `data/summary/final_lowrho_cluster_grid_steps3000_R20_v1_by_combo.csv`

`correlation_summary.csv` resume, para cada serie, el coeficiente de Pearson
entre los 14 pares de medias y sus rangos. Es descriptivo: no demuestra
causalidad, no usa muestras instantáneas y no estima una transición crítica.

## Lectura de nuestros resultados

- En `rho={4,8}`, y casi también en `rho=2`, el sistema permanece conectado en
  una componente geométrica gigante para prácticamente todo el barrido:
  `S>=0.991`, `S>=0.999` y `S>=0.912`, respectivamente, para Vicsek; en el
  votante los mínimos son `0.996`, `0.999` y `0.941`. La polarización, en
  cambio, recorre casi todo `[0,1]`. Por eso la franja horizontal cerca de
  `S=1` significa **conectividad saturada**, no orden polar.
- En las densidades bajas, `S` y `va` recorren juntos una rama diagonal. El
  coeficiente de Pearson entre los 14 pares de medias está entre `0.963` y
  `0.992` para las seis series modelo--densidad bajas. Al aumentar el ruido,
  disminuyen tanto el alineamiento como la fracción reunida en la mayor
  componente geométrica.
- Esa correlación no establece que un cluster grande cause polarización (ni la
  causalidad inversa): ambos observables cambian al variar `eta`. Para estudiar
  precedencia temporal haría falta analizar la correlación conjunta de
  `va(t)` y `S(t)` o retardos, algo que no exige el TP.
- `S` solo informa el tamaño relativo de la mayor componente. No dice cuántos
  clusters hay, cómo se distribuyen sus tamaños, si el cluster es compacto ni
  si sus partículas apuntan en la misma dirección. Es un observable geométrico,
  mientras `va` es un observable global de orientación.
- En densidades bajas la variabilidad entre realizaciones es grande porque
  `N={32,16,11}` y la formación/ruptura de una componente cambia `S` en saltos
  relativos grandes. Esa variabilidad sigue almacenada en los CSV fuente, pero
  no se dibuja en esta versión.

Esta figura es exploratoria y no reemplaza el punto E obligatorio. La figura
oficial mantiene `x=<S>`, `y=<va>` y `rho={2,4,8}` en
`figures/final_production_v1/comparison_va_vs_S.png`. La inclusión formal de
las tres densidades bajas en el punto E sigue pendiente de aclaración docente.

Regeneración:

```bash
MPLCONFIGDIR=/private/tmp/tp2_mplconfig PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache \
  .venv-mpl311/bin/python python/plot_cluster_order_relationship.py
```
