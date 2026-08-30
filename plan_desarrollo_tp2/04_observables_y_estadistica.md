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

- valor o criterio final de `t_eq`;
- cantidad de pasos de medición;
- cantidad `R` de realizaciones;
- semillas;
- desvío o error estándar como barra.

Los valores se deciden después de las corridas preliminares. El plan no fija `R`, tolerancias numéricas ni metas de precisión que no aparecen en el enunciado.

## Tablas mínimas

Por realización:

```text
model,rho,N,eta,seed,t_eq,va_bar,S_bar
```

Por combinación:

```text
model,rho,N,eta,R,va_mean,va_error,S_mean,S_error,error_definition
```

## Fuera de alcance

No se calcula susceptibilidad ni se estima `eta_c`: son análisis complementarios mencionados en bibliografía, pero no pedidos por el TP.

## Criterio de cierre

- [ ] `va(t)` y `S(t)` se calculan sobre el mismo estado.
- [ ] `t_eq` está justificado con series temporales.
- [ ] Primero se promedia en el estacionario y después entre realizaciones.
- [ ] La cantidad de realizaciones y las semillas están registradas.
- [ ] Las barras tienen una definición explícita y constante.

