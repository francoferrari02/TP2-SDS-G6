# Revisión final de alcance contra la cátedra

## Criterio usado

Cada elemento del plan se clasifica como:

- **Requisito:** aparece en el enunciado, la teórica o la aclaración docente.
- **Decisión abierta:** la cátedra exige elegirla y documentarla, pero no fija su valor.
- **Implementación interna:** no agrega un estudio; solo permite construir o verificar lo pedido.
- **Fuera de alcance:** aparece en bibliografía o en el repositorio auditado, pero no se hará.

## Requisitos y ubicación en el plan

| Requisito de cátedra | Dónde se cubre |
|---|---|
| Modelo off-lattice, `L=10`, `rc=1`, `dt=1`, `v=0.03` | etapas 1-2 |
| Densidades `rho=2,4,8`, `N=200,400,800` | README, etapas 1, 5-7 |
| Vicsek: promedio vectorial incluyendo a la propia partícula | etapas 1-3 |
| Votante: copiar otra partícula; aislada conserva dirección más ruido | etapas 1-3 |
| Ruido `U[-eta/2,eta/2]` | etapas 1 y 5 |
| Actualización sincrónica y movimiento con `v(t)` | etapas 1-3 |
| Borde periódico en movimiento, vecinos y clusters | etapas 1-3 |
| Simulación y animación independientes mediante texto | etapas 1-3 y 7 |
| Barrido de varios `eta` para todas las combinaciones | etapas 5-6 |
| Varias realizaciones independientes | etapas 4-6 |
| Series `va(t)` y elección justificada de `t_eq` | etapas 4, 5 y 7B |
| `<va>` vs. `eta` con barras para `rho=2,4,8` | etapa 7C |
| `S(t)` y `<S>` vs. `eta` con barras | etapas 4, 6 y 7D |
| `S=n_max/N`, componente conexa periódica | etapas 2-4 |
| `<va>` en función de `<S>`, distinguiendo tres densidades | etapa 7E |
| Repetir A-E para votante y comparar con Vicsek | etapa 7F |
| Vectores velocidad coloreados por ángulo en animaciones | etapa 7A |
| Tiempos del CIM comparados con TP1 | etapa 8 |
| Presentación de 13 minutos, PDF con links, informe y ZIP liviano | etapa 9 |
| Extender clusters a `1/pi,1/(2pi),1/(3pi)` | README, etapas 6 y 7D |

## Decisiones abiertas, no requisitos numéricos

Se decidirán con corridas preliminares y quedarán registradas:

- valores y separación de `eta`;
- pasos de transitorio y medición;
- cantidad de realizaciones y semillas;
- desvío o error estándar como barra;
- frecuencia y formato exacto de salida;
- entorno y tramo del benchmark.

El plan ya no fija `R=20`, `T=10000`, un rango obligatorio `0..2pi`, una tolerancia de error ni un algoritmo automático para `t_eq`.

## Implementación interna que no amplía el TP

- comparar el CIM con fuerza bruta en casos pequeños para validar vecinos;
- usar BFS/DFS o `union-find` para componentes conexas;
- automatizar la tabla de combinaciones para detectar faltantes;
- probar borde periódico, sincronía, límites de observables y orden de almacenamiento;
- separar archivos escalares de trayectorias para no generar salida pesada innecesaria.

Estas tareas no producen conclusiones ni gráficos adicionales; son controles del código solicitado.

## Elementos explícitamente excluidos

- susceptibilidad y estimación de `eta_c`;
- exponentes críticos y escalado de tamaño finito;
- histéresis;
- distribución de tamaños de clusters;
- barrido continuo de densidad o percolación estática;
- interacción topológica, anisotrópica o por vecinos más cercanos;
- FHP, LGCA, Lattice Boltzmann, obstáculos o fuerzas;
- comparación de CIM contra fuerza bruta como estudio de resultados.

## Ambigüedades reales conservadas

### Alcance del punto E

La aclaración dice extender las densidades “solo para el estudio de Cluster”. El punto D es inequívocamente el estudio de clusters y se amplía a seis densidades. El punto E pide explícitamente distinguir tres densidades, por lo que el plan mínimo mantiene allí `rho=2,4,8`.

Si la cátedra confirma que la aclaración también comprende la relación `<va>` vs. `<S>`, se pueden agregar los tres conjuntos bajos sin modificar el motor ni repetir sus corridas. Hasta entonces no se presenta esa ampliación como requisito.

### Conversión de las densidades bajas a `N`

Con `L=10`, `N=rho L^2` da valores no enteros para `1/pi`, `1/(2pi)` y `1/(3pi)`. El plan usa provisionalmente redondeo al entero más cercano (`32,16,11`) y registra la densidad efectiva, pero esa convención no aparece expresamente en el material y debe confirmarse antes del barrido definitivo de clusters.

## Veredicto

Con las correcciones de esta revisión, el camino principal contiene todos los entregables A-G, la aclaración de clusters y las validaciones mínimas, sin agregar estudios de bibliografía ni fijar decisiones experimentales que la cátedra dejó abiertas.
