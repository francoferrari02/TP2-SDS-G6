# Etapa 1 - Especificación congelada y arquitectura

## Objetivo

Convertir el enunciado y la teoría en contratos ejecutables antes de escribir el motor. La salida de esta etapa evita que una decisión accidental de implementación se convierta luego en “la definición” del modelo.

## Estado y parámetros

Para cada partícula `i` se guardan:

```text
id estable, x_i, y_i, theta_i
```

La velocidad se deriva, no necesita almacenarse:

```text
vx_i = v cos(theta_i)
vy_i = v sin(theta_i)
```

Parámetros vinculantes:

| Parámetro | Valor |
|---|---:|
| `L` | 10 |
| `rc` | 1 |
| `dt` | 1 |
| `v` | 0.03 |
| contorno | periódico |
| `rho` base | 2, 4, 8 |
| `N` base | 200, 400, 800 |

Condición inicial: posiciones independientes uniformes en `[0,L)^2` y ángulos independientes uniformes en `[0,2pi)`.

## Distancia y vecindad

Para cada componente:

```text
dx = x_j - x_i - L round((x_j-x_i)/L)
dy = y_j - y_i - L round((y_j-y_i)/L)
d2 = dx*dx + dy*dy
```

Hay una arista geométrica si `d2 <= rc*rc`. La lista base de vecinos externos excluye a `i`; cada regla decide explícitamente qué hacer con la propia partícula.

## Un paso temporal vinculante

Con el estado completo en `t`:

1. Construir vecinos a partir de `x(t)`.
2. Calcular todas las orientaciones `theta_new` desde `theta(t)`.
3. Calcular todas las posiciones `x_new` usando `theta(t)`, no `theta_new`.
4. Aplicar módulo `L` a `x_new` e `y_new`.
5. Confirmar juntos `x_new` y `theta_new` como estado `t+1`.

Pseudocódigo:

```text
neighbors = build_neighbors(x_old)
for i in stable_id_order:
    base_heading[i] = interaction(model, i, theta_old, neighbors)
    theta_new[i] = wrap_angle(base_heading[i] + noise(seed,t,id))

for i:
    x_new[i] = periodic(x_old[i] + v*cos(theta_old[i])*dt)
    y_new[i] = periodic(y_old[i] + v*sin(theta_old[i])*dt)

commit(x_new, theta_new)
```

## Reglas de orientación

### Vicsek

Promediar vectorialmente `{i} union vecinos_externos(i)`:

```text
C = sum cos(theta_j)
S = sum sin(theta_j)
theta_base = atan2(S,C)
theta_new = theta_base + U[-eta/2,eta/2]
```

No promediar ángulos aritméticamente.

### Votante ruidoso

```text
if vecinos_externos(i) no está vacío:
    j = elección uniforme entre vecinos_externos(i)
    theta_base = theta_j(t)
else:
    theta_base = theta_i(t)
theta_new = theta_base + U[-eta/2,eta/2]
```

La elección y el ruido se hacen para cada partícula y paso desde el estado viejo.

En ambos modelos, el ruido es independiente para cada partícula y cada paso temporal, como indica la teórica.

## Arquitectura sugerida de implementación

Esta separación no es una exigencia de nombres o carpetas de la cátedra. Su único requisito arquitectónico explícito es independizar simulación y animación mediante archivos de texto.

```text
core/
  state                 tipos y parámetros
  periodic_geometry     wrap y distancia mínima
  neighbor_search       interfaz y CIM
  rules                 Vicsek y votante
  simulation            actualización sincrónica/backward
  observables           va y S
  rng                    streams reproducibles
  text_output            trayectoria y escalares
cli/
  simulate              parseo, validación y ejecución
python/
  run_sweep              manifiesto y corridas
  aggregate              estadística entre realizaciones
  plot                   figuras
  animate                lector independiente de trayectoria
tests/
```

No duplicar dos motores. `model` cambia únicamente la regla de orientación.

## Reproducibilidad

- Cada realización usa una semilla explícita y registrada; no se siembra por reloj.
- La implementación debe respetar actualización sincrónica y no depender del orden de almacenamiento.
- La forma concreta de organizar los generadores aleatorios es una decisión interna, siempre que pase esas verificaciones.

## Interfaz de ejecución sugerida

```text
simulate --model vicsek|voter --rho RHO --eta ETA --steps T --seed S
         --scalar-out PATH [--trajectory-out PATH|none]
         [--scalar-stride K] [--trajectory-stride K]
```

Los nombres de opciones no son fijados por la cátedra. Lo obligatorio es ejecutar de forma reproducible ambos modelos con los parámetros pedidos y registrar ruido, densidad, duración y semilla.

## Formatos de texto

### Escalares sugeridos

```text
t va S
0 0.0712 0.84
1 0.0831 0.86
```

### Trayectoria obligatoria en texto

```text
t id x y vx vy
0 0 ...
0 1 ...
```

El formato exacto no está fijado. Debe ser simple, estable y documentar como mínimo el tiempo y las posiciones/velocidades necesarias para que la animación reconstruya cada cuadro sin ejecutar el motor. Para el barrido pueden guardarse solo las series escalares y reservar las trayectorias completas para los casos animados.

## Criterio de cierre

- [ ] Existe un documento/configuración con todas las convenciones anteriores.
  - Estado: en progreso. Las convenciones del modelo están documentadas; todavía falta congelar mediante evidencia el protocolo experimental y el formato final de salida.
- [x] La representación base del estado (`Parameters` y `Particle`) fue implementada en `src/core/model.hpp`.
  - Evidencia: `cmake -S . -B build && cmake --build build` compila la biblioteca base y el test geométrico.
- [ ] El formato de salida está documentado y permite una animación independiente.
- [ ] Las semillas son explícitas y el resultado no depende del orden de almacenamiento.
- [ ] El equipo puede explicar con un ejemplo la diferencia entre mover con `theta(t)` y con `theta(t+1)`.
- [ ] No queda ninguna decisión de modelo heredada implícitamente del TP1 o del repositorio externo.
