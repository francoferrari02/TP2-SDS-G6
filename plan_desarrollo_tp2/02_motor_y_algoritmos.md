# Etapa 2 - Motor, búsqueda de vecinos y clusters

## Objetivo

Implementar un motor correcto y reutilizable. La optimización se apoya en un oráculo de fuerza bruta para tests; nunca se optimiza una regla no validada.

## Orden recomendado de implementación

1. Tipos, parámetros y estado.
2. Geometría periódica.
3. Búsqueda de vecinos por fuerza bruta como referencia.
4. Cell Index Method (CIM).
5. Regla Vicsek.
6. Regla votante.
7. Paso sincrónico/backward.
8. Polarización.
9. Componente gigante.
10. Escritura de texto y CLI.

## Cell Index Method

Reutilizar el criterio válido del CIM desarrollado en TP1: la longitud de celda y la cantidad de celdas vecinas inspeccionadas deben garantizar que ningún par con `d <= rc` quede afuera. La cátedra no fija un valor de `M`; se elige, documenta y valida contra una referencia pequeña.

Procedimiento:

1. Vaciar y reconstruir las celdas desde `x(t)`.
2. Recorrer pares de celdas sin duplicar combinaciones.
3. Para cada par candidato, evaluar distancia mínima periódica.
4. Si `d2 <= rc^2`, agregar la arista a ambas listas y ejecutar `union(i,j)`.

Requisitos:

- No duplicar vecinos.
- No incluir `i` en la lista externa.
- Mantener simetría: `j in N_i` si y solo si `i in N_j`.
- Evitar `sqrt`: comparar distancias al cuadrado.

## Clusters

El cluster es conectividad transitiva, no “todas las partículas dentro de un mismo disco”. A partir de las aristas de vecinos se obtienen las componentes conexas y luego:

```text
n_max = tamaño de la componente más grande
S = n_max/N
```

La guía teórica admite BFS/DFS sobre la lista de vecinos o `union-find`. El plan no impone una de esas alternativas; se elige la más simple de integrar y se valida con casos conocidos. El borde periódico debe estar resuelto al generar las aristas.

## Paso del motor

Mantener buffers separados:

```text
x_old, y_old, theta_old
x_new, y_new, theta_new
```

La fase de orientación no escribe el estado viejo. La fase de movimiento usa únicamente `theta_old`. Recién al final se intercambian buffers.

Un diseño válido puede guardar un solo vector de partículas y buffers auxiliares, siempre que ningún campo viejo se sobrescriba antes de haber calculado todas las salidas que dependen de él.

## Observables en el motor

Polarización:

```text
va = hypot(sum cos(theta_i), sum sin(theta_i)) / N
```

Componente gigante:

```text
S = n_max/N
```

Calcular `va(t)` y `S(t)` sobre el mismo estado temporal. Si el paso reconstruye vecinos desde `x(t)` pero ya confirmó `x(t+1)`, no reutilizar una lista desfasada para rotular `S(t+1)`. La opción más clara es medir antes de avanzar o exponer una operación `measure_current_state()` que garantice sincronía.

## Salidas y costo

- El escritor de trayectoria se puede apagar por completo.
- El log escalar puede escribirse cada paso o con *stride*; para justificar estacionariedad conviene cada paso en pilotos.
- Comprobar errores de apertura/escritura.
- El motor no crea gráficos ni depende de Matplotlib.

## Riesgos específicos

- Usar `theta_new` al mover.
- Incluir a `i` en la lista externa y volver a incluirla en Vicsek.
- Permitir autoelección en votante.
- Aplicar borde periódico a posiciones pero no a vecinos/clusters.
- Medir `S` con la vecindad del paso anterior.
- Consumir RNG en orden de almacenamiento y romper la prueba de permutación.
- Construir mal las componentes por confundir vecinos directos con conectividad transitiva.
- Usar `< rc` cuando la especificación dice `<= rc`.

## Criterio de cierre

- [ ] Ambos modelos comparten el mismo motor y solo bifurcan en la regla de orientación.
- [ ] El CIM coincide exactamente con fuerza bruta en configuraciones pequeñas.
- [ ] `S` usa las mismas aristas periódicas que la interacción.
- [ ] Se puede ejecutar sin trayectoria y con log escalar.
- [ ] Todas las salidas incluyen parámetros y semilla.
- [ ] El código queda listo para la suite de la etapa 3, pero todavía no se autoriza producción.
