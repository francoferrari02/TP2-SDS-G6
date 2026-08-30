# Etapa 7 - Figuras y animaciones obligatorias

## Objetivo

Generar únicamente los estudios A-E para ambos modelos y la comparación F indicados por el enunciado.

## A. Animaciones características

- Un vector por partícula, ubicado en su posición.
- Dirección y módulo dados por su velocidad.
- Color asociado al ángulo.
- Módulo de animación independiente que lee la salida de texto.
- Pocos casos representativos; las notas del profesor sugieren dos casos bien distintos, de ruido bajo y alto.

Las animaciones deben abrir cada estudio en la presentación. El PDF lleva links explícitos y no las embebe.

## B. Evolución temporal de polarización

Para cada densidad `rho=2,4,8` y situaciones características de `eta`:

- graficar `va(t)`;
- comparar Vicsek y votante bajo el mismo protocolo;
- marcar `t_eq` con una línea vertical;
- explicar la ventana usada para el promedio estacionario.

## C. Polarización estacionaria vs. ruido

```text
x = eta
y = <va>_est
densidades = {2,4,8}
modelos = {vicsek,voter}
barras = definición declarada del protocolo
```

Las tres densidades deben distinguirse claramente mediante curvas o paneles comparables.

## D. Estudio de clusters

Para ambos modelos:

1. graficar `S(t)` en situaciones características;
2. marcar la misma ventana estacionaria usada para `va`;
3. graficar `<S>_est` vs. `eta` con barras de error.

Este punto incluye:

```text
rho = {2,4,8,1/pi,1/(2pi),1/(3pi)}
```

Se recomienda separar densidades base y adicionales en paneles para mantener legibilidad, sin agregar otro estudio.

## E. Relación entre orden y conectividad

El enunciado pide polarización en función de componente gigante:

```text
x = <S>_est
y = <va>_est
cada punto = un eta del barrido
densidades = {2,4,8}
```

Distinguir densidades y modelos. `eta` no es un eje. Este gráfico estudia si conectividad espacial y alineamiento global se relacionan, pero no presupone el resultado.

La ampliación a las tres densidades bajas no se incluye como obligación porque el punto E dice explícitamente “distinguir las tres densidades”. Solo se hará si la cátedra confirma que la aclaración de clusters también abarca este punto.

## F. Comparación entre modelos

Repetir A-E para el votante y comparar contra Vicsek usando:

- mismos parámetros;
- misma grilla de ruido;
- mismo criterio de estacionario;
- misma cantidad de realizaciones;
- misma definición de barras.

## Convenciones de presentación

- `va` y `S` se muestran en su rango `[0,1]`.
- Colores, líneas y marcadores identifican siempre de la misma forma modelo y densidad.
- Cada epígrafe declara `rho`, `eta` cuando corresponda, `R` y significado de barras.
- No se suavizan datos ni se agregan ajustes no solicitados.

La copia de la Guía de Presentaciones incluida en el repositorio de referencia agrega controles de formato que sí son coherentes con la documentación citada por el enunciado:

- en la presentación, la figura no lleva título interno ni *caption*; los parámetros se escriben al costado de la figura;
- los ejes se rotulan preferentemente con palabras y unidades cuando correspondan;
- letras y números dentro de la figura deben tener tamaño legible, al menos 20 para las diapositivas;
- cada dato promedio debe distinguirse con un símbolo o su barra; una línea recta puede usarse como guía visual, pero no una interpolación arbitraria;
- para el PDF se usa un fotograma representativo y un enlace explícito; durante la exposición en vivo la animación debe quedar integrada en la diapositiva, sin salir a otro programa.

El repositorio externo afirma además que la cátedra pidió figuras sin grilla de fondo, `va` y `S` separados y cada modelo individual antes de la superposición comparativa. Mantener estas indicaciones como pendientes de confirmación: no cambian el barrido ni bloquean la generación de tablas, pero sí el diseño visual final.

## Fuera de alcance

No generar susceptibilidad, `eta_c`, histéresis, distribución de tamaños de cluster ni curva de percolación. Ninguna reemplaza los gráficos A-E.

## Progreso parcial (2026-08-30): figuras diagnósticas de Vicsek

Se agregó `python/vicsek_eta_study_plot.py`, siguiendo la estructura de los scripts del votante pero ajustado a la decisión vigente de barras: las curvas estacionarias usan error estándar (`va_stderr`, `S_stderr`) y las series temporales muestran bandas de error estándar. La dependencia externa es `matplotlib`; en esta máquina se instaló con:

```text
python3 -m pip install --user matplotlib==3.8.4
```

Entrada usada:

```text
data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_by_combo.csv
data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_series_sampled.csv
```

Comandos verificados:

```text
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 -m py_compile python/pilot_analyze.py python/vicsek_eta_study_plot.py
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/pilot_analyze.py --run-name vicsek_eta0_6_deta0p5_steps3000_R20_v1 --sample-stride 50 --t-eq 1500
PYTHONPYCACHEPREFIX=/private/tmp/tp2_pycache python3 python/vicsek_eta_study_plot.py --run-name vicsek_eta0_6_deta0p5_steps3000_R20_v1 --t-eq 1500
```

Evidencia:

- `pilot_analyze.py` releyó `780` observables, `780` válidos, `0` problemas.
- `data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_series_sampled.csv` ahora guarda `va(t)` y `S(t)`, con desvío y error estándar, por lo que las series de clusters se pueden regenerar desde datos livianos versionados.
- Se generaron `11` PNG en `figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/`: `va_vs_eta.png`, `S_vs_eta.png`, sus zooms `eta<=1.5`, `va_vs_S.png`, y `va_t_*/S_t_*` para `rho=2,4,8`.
- Se revisaron visualmente `va_vs_eta.png`, `S_t_rho_2.png` y `va_vs_S.png`: los archivos renderizan, los ejes cubren `[0,1]`, aparecen las barras/bandas y las series marcan `t_eq=1500`.

Alcance: esto no cierra la etapa 7. Falta integrar el votante bajo el mismo estilo estadístico, completar la comparación Vicsek-votante, decidir el formato final de diapositivas, generar/validar animaciones y cubrir las densidades bajas del punto D para Vicsek si el grupo conserva esa obligación.

## Criterio de cierre

- [ ] Hay animaciones independientes con vectores coloreados por ángulo.
- [ ] `va(t)` y `S(t)` muestran y justifican `t_eq`.
  - Estado: en progreso. Para Vicsek (`rho=2,4,8`, `eta=0..6` con paso `0.5`, `R=20`, `steps=3000`) ya existen series `va_t_*` y `S_t_*` con `t_eq=1500` graficado; falta justificar si ese corte queda como definitivo para Vicsek y repetir/comparar con votante.
- [ ] `<va>` vs. `eta` cubre ambos modelos y `rho=2,4,8`.
  - Estado: en progreso. Para Vicsek ya existe `figures/vicsek_eta0_6_deta0p5_steps3000_R20_v1/va_vs_eta.png`; falta la versión comparativa con votante bajo protocolo común.
- [ ] `<S>` vs. `eta` incorpora las densidades adicionales solo en clusters.
  - Estado: en progreso parcial. Para Vicsek base (`rho=2,4,8`) ya existe `S_vs_eta.png`; faltan las densidades bajas del punto D para Vicsek si se mantienen dentro del alcance del grupo.
- [ ] `<va>` vs. `<S>` usa `S` en x, `va` en y y las tres densidades base.
  - Estado: en progreso. Para Vicsek ya existe `va_vs_S.png`; falta comparación contra votante y revisión del formato final.
- [ ] Todos los gráficos tienen barras definidas cuando corresponde.
  - Estado: en progreso. Las figuras nuevas de Vicsek usan error estándar, consistente con `DECISIONES_PENDIENTES.md`; queda revisar que las figuras/scripts del votante usen la misma convención antes de congelar la comparación final.
- [ ] Vicsek y votante se comparan bajo el mismo protocolo.
- [ ] Las exportaciones para diapositivas cumplen tamaños de fuente, ejes, símbolos y ubicación de parámetros de la guía.
- [ ] La versión para exposición integra las animaciones y el PDF usa fotogramas con links probados.
