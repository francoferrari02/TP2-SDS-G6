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

## Interfaz de ejecución (implementada)

```text
simulate
  --model vicsek|voter
  --rho-nominal RHO
  --rho-label LABEL
  --N N
  --eta ETA
  --steps T
  --base-seed SEED
  --realization R
  --output-dir PATH
  [--write-trajectory]
  [--observables-stride K]
  [--trajectory-stride K]
  [--overwrite]
```

Implementada en `src/cli/simulate.cpp` (ejecutable `simulate`) sobre la lógica reutilizable de `src/cli/simulate_cli.hpp` (`parse_arguments`/`execute_run`). `L`, `rc`, `dt` y `v` no son opciones: son las "reglas que no se negocian" del TP y se usan los valores por defecto de `Parameters`. `N` se recibe explícitamente y nunca se recalcula a partir de `rho-nominal` (solo se verifica consistencia para `rho=2,4,8`). Una revisión posterior reforzó la validación de entradas (`--rho-nominal`/`--eta` rechazan `NaN`/`inf`; `--rho-label` usa una lista blanca de caracteres seguros para nombre de directorio) y la robustez de la publicación de archivos (ver "Publicación atómica de archivos" en `02_motor_y_algoritmos.md`, incluida la limitación de atomicidad entre dos archivos que queda documentada, no resuelta). Detalle completo de la interfaz, validaciones y ejemplo de ejecución en `02_motor_y_algoritmos.md`.

## Formatos de texto (implementado)

Formato congelado (decisión resuelta, ver `DECISIONES_PENDIENTES.md`, sección "Decisiones resueltas"). Los esbozos anteriores de esta sección (`t va S` separado por espacios y `t id x y vx vy`) quedan reemplazados por el contrato real:

Cada corrida escribe su propio directorio:

```text
output/<modelo>/<rho_label>/eta_<eta>/steps_<T>/realization_<R>_seed_<SEED>/
  observables.csv
  trajectory.csv
```

`observables.csv` siempre existe; `trajectory.csv` solo si se pidió `--write-trajectory`. Ambos son CSV UTF-8 (separador `,`, punto decimal, locale `C`), con un bloque de metadatos `# clave=valor` autocontenido (18 claves) seguido del encabezado (`t,va,S` o `t,id,x,y,theta`) y los datos. `theta` reemplaza a `vx,vy` (se reconstruye con `v`, ya en la cabecera). Implementado en `src/core/text_output.hpp` (serialización) y `src/cli/simulate_cli.hpp`/`src/cli/simulate.cpp` (orquestación: directorios, no sobrescritura por defecto, escritura atómica). Detalle completo, con los 18 metadatos, la semántica de strides y la interfaz de la CLI, en `02_motor_y_algoritmos.md`.

Lo que sigue sin definir es la **frecuencia productiva** de muestreo (qué valores concretos de stride se usarán en el barrido definitivo), no el formato en sí.

## Criterio de cierre

- [ ] Existe un documento/configuración con todas las convenciones anteriores.
  - Estado: en progreso. Las convenciones del modelo y el formato de salida están documentados y congelados; todavía falta el protocolo experimental (grilla de `eta`, `t_eq`, realizaciones, barras de error, valores productivos de stride).
- [x] La representación base del estado (`Parameters` y `Particle`) fue implementada en `src/core/model.hpp`.
  - Evidencia: `cmake -S . -B build && cmake --build build` compila la biblioteca base y el test geométrico.
- [x] El formato de salida está documentado y permite una animación independiente.
  - Evidencia: `src/core/text_output.hpp`, `src/cli/simulate_cli.hpp`, `src/cli/simulate.cpp`; `tests/test_text_output.cpp` y `tests/test_cli_simulate.cpp` (17 casos en la versión actual), registrados en CTest. `trajectory.csv` guarda `t,id,x,y,theta` por partícula y paso, suficiente para reconstruir cada cuadro de la animación sin ejecutar el motor (ver `02_motor_y_algoritmos.md`).
- [ ] Las semillas son explícitas y el resultado no depende del orden de almacenamiento.
- [ ] El equipo puede explicar con un ejemplo la diferencia entre mover con `theta(t)` y con `theta(t+1)`.
- [ ] No queda ninguna decisión de modelo heredada implícitamente del TP1 o del repositorio externo.
