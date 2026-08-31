# Etapa 4 - Observables, estacionario y realizaciones

## Objetivo

Aplicar exactamente el procedimiento pedido: obtener series temporales, identificar el inicio estacionario, promediar cada realización en esa ventana y después promediar varias realizaciones independientes.

## Series requeridas

Para cada realización `r` y combinación `(modelo,rho,eta)` guardar:

```text
va_r(t), S_r(t)
```

con:

```text
va(t) = hypot(sum_i cos(theta_i), sum_i sin(theta_i))/N
S(t) = n_max(t)/N
```

Los dos observables deben corresponder al mismo estado temporal.

## Promedio estacionario por realización

Elegido `t_eq` a partir de las series temporales:

```text
va_bar_r = mean_{t>=t_eq} va_r(t)
S_bar_r  = mean_{t>=t_eq} S_r(t)
```

La misma ventana estacionaria se usa para `va` y `S` dentro de una corrida.

## Promedio entre realizaciones

Con `R` realizaciones independientes:

```text
<va> = mean_r va_bar_r
<S>  = mean_r S_bar_r
```

Las muestras temporales de una misma corrida no se cuentan como realizaciones independientes.

## Barras de error

La cátedra no fija una única definición. Antes del barrido final se debe elegir y declarar una de estas opciones indicadas en la guía teórica:

- desvío estándar entre las medias de las realizaciones, para mostrar variabilidad;
- error estándar de esas medias, para mostrar precisión del promedio.

La definición elegida debe mantenerse para ambos modelos y todas las densidades. También se registra `R` en figuras o epígrafes.

## Cómo elegir `t_eq`

El material no prescribe un algoritmo automático. El procedimiento mínimo requerido es:

1. hacer corridas preliminares para situaciones características de ruido y densidad;
2. graficar `va(t)` y `S(t)`;
3. identificar desde qué instante dejan de mostrar una tendencia de relajación y fluctúan alrededor de un régimen estable;
4. marcar ese `t_eq` con una línea vertical;
5. fijar y documentar el criterio que se usará en el barrido.

No se adopta automáticamente “descartar el 50%” ni se exige análisis de autocorrelación, porque la cátedra no establece esos procedimientos.

## Decisiones pendientes que deben registrarse

- valores o criterios finales de `t_eq` que falten para bloques todavía no corridos;
- cantidad de pasos de medición de bloques todavía no cerrados;
- cantidad `R` de realizaciones y semillas de bloques todavía no cerrados;
- valores concretos de stride productivo;
- cualquier extensión que dependa de densidades bajas no confirmadas.

Los valores se deciden después de las corridas preliminares. El plan no fija tolerancias numéricas ni metas de precisión que no aparecen en el enunciado.

## Protocolo estadístico fijado para la matriz base

Para las densidades obligatorias `rho=2,4,8`, ambos modelos usan ahora el
mismo protocolo temporal y estadístico:

```text
steps = 3000
R = 20 realizaciones independientes
t_eq = 1500
ventana estacionaria = t=1500..3000
barra de error = desvío estándar entre medias estacionarias de realizaciones
```

En el votante esto ya estaba registrado como decisión previa. El 2026-08-30
se formalizó también para Vicsek porque las corridas diagnósticas existentes
(`vicsek_eta0_6_deta0p5_steps3000_R20_v1`) ya usaban ese protocolo de hecho:
`python/pilot_analyze.py` releyó `780/780` archivos válidos con `0` problemas
y las series `va(t)`/`S(t)` generadas con `t_eq=1500` muestran que el corte
es conservador respecto de la relajación observada. La comparación final
queda metodológicamente más simple al mantener la misma ventana que el
votante.

## Tablas mínimas

Por realización:

```text
model,rho,N,eta,seed,t_eq,va_bar,S_bar
```

Por combinación:

```text
model,rho,N,eta,R,va_mean,va_error,S_mean,S_error,error_definition
```

## Progreso parcial (2026-08-30): resumen temporal con `S(t)`

`python/pilot_analyze.py` ahora escribe en `data/summary/<run_name>_series_sampled.csv` tanto `va(t)` como `S(t)`, cada uno con desvío entre realizaciones y error estándar (`va_stdev`, `va_stderr`, `S_stdev`, `S_stderr`). Esto corrige la salida real para que coincida con el propósito documentado del analizador y permite regenerar figuras de `S(t)` desde datos livianos versionados, sin depender de `data/pilots/`, que queda fuera de git.

Evidencia: se regeneró `data/summary/vicsek_eta0_6_deta0p5_steps3000_R20_v1_series_sampled.csv` con `780/780` observables válidos, `0` problemas y ventana estacionaria explícita `--t-eq 1500`.

## Fuera de alcance

No se calcula susceptibilidad ni se estima `eta_c`: son análisis complementarios mencionados en bibliografía, pero no pedidos por el TP.

## Criterio de cierre

- [ ] `va(t)` y `S(t)` se calculan sobre el mismo estado.
- [ ] `t_eq` está justificado con series temporales.
  - Estado: resuelto para la matriz base `rho=2,4,8` de ambos modelos con `t_eq=1500`; siguen fuera de este cierre los bloques que dependan de densidades bajas no confirmadas o corridas faltantes.
- [ ] Primero se promedia en el estacionario y después entre realizaciones.
- [ ] La cantidad de realizaciones y las semillas están registradas.
  - Estado: `R=20` y `steps=3000` quedaron formalizados para votante y Vicsek en `DECISIONES_PENDIENTES.md`; las semillas quedan trazadas en manifiestos/scripts de cada estudio.
- [ ] Las barras tienen una definición explícita y constante.
  - Estado: resuelto como desvío estándar entre realizaciones; las figuras que usen error estándar deben regenerarse antes de entrega.
