# Hoja de ruta maestra - TP2 de bandadas off-lattice

## Objetivo

Desarrollar desde cero un motor reproducible para los modelos de Vicsek y votante ruidoso, validarlo antes de producir datos, ejecutar los barridos requeridos y generar las figuras, animaciones, comparación de rendimiento e informe del TP2.

Esta carpeta es el punto de entrada operativo para humanos y agentes. Cada etapa tiene entradas, tareas, pruebas y un criterio de cierre. Una etapa no se considera terminada porque el código compile: debe satisfacer su evidencia de aceptación.

## Fuentes vinculantes

Leer, en este orden, antes de implementar:

1. [`../bibliografia/enunciado_tp2_guia_de_trabajo.md`](../bibliografia/enunciado_tp2_guia_de_trabajo.md)
2. [`../bibliografia/teoria_tp2_automatas_off_lattice.md`](../bibliografia/teoria_tp2_automatas_off_lattice.md)
3. [`../bibliografia/fuentes_recomendadas_tp2.md`](../bibliografia/fuentes_recomendadas_tp2.md)

El repositorio externo auditado sirve para detectar aciertos y errores, no como especificación ni como fuente de resultados. La auditoría está en [`00_auditoria_referencia_y_notas.md`](00_auditoria_referencia_y_notas.md).

La comprobación requisito por requisito está en [`REVISION_FINAL_DE_ALCANCE.md`](REVISION_FINAL_DE_ALCANCE.md).

Las elecciones que todavía no pueden asumirse están centralizadas en [`DECISIONES_PENDIENTES.md`](DECISIONES_PENDIENTES.md).

Mapa rápido del contexto teórico:

| Tema de desarrollo | Sección de la guía teórica |
|---|---|
| estado, parámetros y condición inicial | secciones 1-2 |
| distancia mínima y vecinos periódicos | sección 3 |
| Vicsek y actualización sincrónica/backward | sección 4 |
| votante y conversión de la convención de ruido | secciones 5-5.1 |
| polarización | sección 6 |
| transitorio, realizaciones y barras | sección 7 |
| clusters/componente gigante | sección 8 |
| controles físicos esperables | sección 9 |

## Reglas que no se negocian

- Espacio continuo, caja periódica cuadrada: `L=10`.
- `rc=1`, `dt=1`, `v=0.03`.
- Densidades obligatorias: `rho=2,4,8`, por lo que `N=200,400,800`.
- Ruido de cátedra: `xi ~ U[-eta/2, eta/2]`; `eta` se expresa en radianes.
- Actualización sincrónica.
- Movimiento *backward*: `x(t+1)=x(t)+v(t) dt`; la orientación nueva afecta el desplazamiento siguiente.
- Vicsek incluye a la propia partícula en el promedio vectorial.
- Votante elige otra partícula dentro de `rc`; si no existe, conserva su orientación y solo suma ruido.
- Vecindad y clusters usan distancia mínima periódica y el criterio `d <= rc`.
- El motor escribe texto; análisis y animación son consumidores independientes.
- Ningún barrido definitivo comienza mientras fallen las validaciones de la etapa 3.

## Alcance de densidades

La matriz principal es:

```text
{vicsek, voter} x {2, 4, 8} x {todos los eta finales} x {R realizaciones}
```

Solo para el estudio de clusters se agregan:

```text
rho nominal = {1/pi, 1/(2pi), 1/(3pi)}
```

Con `L=10`, esas densidades producen un `N` no entero. La convención provisional de bajo riesgo es redondear al entero más cercano:

| rho nominal | N redondeado | rho efectiva N/L^2 |
|---:|---:|---:|
| `1/pi = 0.31831...` | 32 | 0.32 |
| `1/(2pi) = 0.15915...` | 16 | 0.16 |
| `1/(3pi) = 0.10610...` | 11 | 0.11 |

Antes del barrido definitivo conviene confirmar este redondeo con la cátedra. En cualquier caso se guardarán `rho_nominal`, `N` y `rho_efectiva`; no se presentará `N=32` como densidad exactamente igual a `1/pi`.

La extensión se aplica al punto D del enunciado: `S(t)` y `<S>` vs. `eta`. La curva `<va>` vs. `eta` y el gráfico `<va>` vs. `<S>` conservan las tres densidades explícitamente indicadas por el enunciado: `rho=2,4,8`. Si la cátedra confirma que “estudio de clusters” también amplía el punto E, ese gráfico puede reutilizar las corridas de densidad baja, pero no se lo incluye como obligación en este plan.

## Etapas y puertas de calidad

| Etapa | Estado | Documento | Producto que habilita avanzar |
|---:|:---:|---|---|
| 0 | [x] | [`00_auditoria_referencia_y_notas.md`](00_auditoria_referencia_y_notas.md) | Auditoría y seguimiento externo actualizados hasta `413dcef` (29/08) |
| 1 | [ ] | [`01_especificacion_y_arquitectura.md`](01_especificacion_y_arquitectura.md) | Contrato del modelo, interfaz y formatos de salida acordados |
| 2 | [ ] | [`02_motor_y_algoritmos.md`](02_motor_y_algoritmos.md) | Motor de ambos modelos y búsqueda de vecinos implementados |
| 3 | [ ] | [`03_validaciones.md`](03_validaciones.md) | Suite mínima completa en verde; permiso para hacer pilotos |
| 4 | [ ] | [`04_observables_y_estadistica.md`](04_observables_y_estadistica.md) | Estimadores, `t_eq`, realizaciones y barras de error definidos |
| 5 | [ ] | [`05_pilotos_y_grilla_eta.md`](05_pilotos_y_grilla_eta.md) | Grilla final de ruido y duraciones justificadas con series temporales |
| 6 | [ ] | [`06_barrido_de_produccion.md`](06_barrido_de_produccion.md) | Matriz completa, trazable y sin combinaciones faltantes |
| 7 | [ ] | [`07_figuras_y_animaciones.md`](07_figuras_y_animaciones.md) | Todas las figuras obligatorias y animaciones verificadas |
| 8 | [ ] | [`08_rendimiento_cim.md`](08_rendimiento_cim.md) | Comparación TP1/TP2 metodológicamente interpretable |
| 9 | [ ] | [`09_informe_presentacion_entrega.md`](09_informe_presentacion_entrega.md) | Informe, exposición, enlaces y ZIP final listos |
| 10 | [x] | [`10_protocolo_para_agentes.md`](10_protocolo_para_agentes.md) | Reglas de delegación, handoff y definición de terminado establecidas |

### Progreso parcial dentro de etapas todavía abiertas

- **Etapa 2:** en progreso. Están implementadas y probadas la búsqueda de vecinos por fuerza bruta (`src/core/neighbor_search.hpp`, `brute_force_neighbors`, oráculo de referencia), el Cell Index Method (`cell_index_neighbors`, validado exhaustivamente contra el oráculo), las reglas de orientación de Vicsek y votante (`src/core/rules.hpp`, `vicsek_update`/`voter_update`) y el paso temporal sincrónico/backward completo (`src/core/time_step.hpp`, `advance_time_step`, que combina vecinos + orientación + movimiento + borde periódico para ambos modelos). Evidencia: `ctest --test-dir build --output-on-failure` (`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`, los cinco en verde). Faltan los observables `va`/`S`, la construcción de clusters con `union-find`, la escritura de texto y la CLI. Detalle completo en [`02_motor_y_algoritmos.md`](02_motor_y_algoritmos.md).
- **Etapa 3:** en progreso. Quedaron cerrados (`[x]`): "CIM contra fuerza bruta" (13 casos), "Vicsek y votante satisfacen reglas distintas" (14 casos sobre el cálculo de orientación, incluyendo invarianza al orden de almacenamiento) y "Sincronía y movimiento backward" (13 casos sobre el paso temporal completo, incluyendo el caso mínimo obligatorio `x_new=0.03, y_new=0, theta_new=pi/2` y la permutación de partículas con ruido no nulo). El resto de las validaciones de la etapa (vecinos medios vs. teoría, `va`/`S`, salida y reproducibilidad de archivos) siguen sin implementarse porque dependen de piezas del motor que todavía no existen (clusters, observables, escritor de texto). Detalle en [`03_validaciones.md`](03_validaciones.md).

## Decisiones experimentales que la cátedra deja abiertas

El plan no fija números que no aparecen en el material. Antes del barrido definitivo el grupo debe elegir, registrar y mantener constantes:

- grilla de valores de `eta`;
- cantidad de pasos de transitorio y de medición;
- cantidad de realizaciones independientes y lista de semillas;
- definición de las barras de error: desvío entre realizaciones o error estándar;
- frecuencia/formato de escritura;
- entorno y tramo cronometrado en la comparación con TP1.

Estas decisiones se toman con corridas preliminares y series temporales, tal como pide la guía. No se presentan como valores impuestos por la cátedra.

## Fuera de alcance del camino principal

No se planifican susceptibilidad, estimación de `eta_c`, exponentes críticos, histéresis, distribución de tamaños de cluster, barrido de percolación estática, interacción topológica ni estudios de tamaño finito. Pueden mencionarse como contexto bibliográfico, pero no se implementan ni sustituyen los gráficos A-G solicitados.

## Estructura objetivo del repositorio

```text
src/                 motor C++
tests/               pruebas unitarias, integración y regresión
python/              barrido, análisis y animación
config/              protocolo y grillas versionadas
data/raw/            salidas por realización (ignorado por git)
data/summary/        tablas agregadas reproducibles
figures/             gráficos finales
animations/          productos de visualización
docs/                bitácora de decisiones y entregables
```

## Registro interno de decisiones

Antes de ejecutar producción debe existir una tabla interna con los parámetros fijos, grilla de `eta`, `t_eq`, pasos medidos, cantidad de realizaciones, semillas, definición de barras, frecuencia de muestreo y formato de salida. Es una forma de conservar las decisiones que el enunciado pide elegir; no es un entregable adicional de la cátedra.
