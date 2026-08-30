# Informe de avance - TP2

Este archivo funciona como bitácora acumulativa del desarrollo del Trabajo
Práctico 2 de Simulación de Sistemas. Registra qué se implementó, cómo se
verificó y qué partes todavía no se desarrollaron.

El informe se actualiza por bloques a medida que avanza el proyecto. Las
secciones de implementación y validación describen el estado alcanzado en
cada momento; por eso una frase histórica puede mencionar una tarea que luego
se desarrolla en una sección posterior.

## Objetivo del trabajo

El TP consiste en simular bandadas de partículas que se mueven en un espacio
continuo, dentro de una caja cuadrada con bordes periódicos. Se deben comparar
dos reglas de interacción: el modelo de Vicsek, que promedia las direcciones
de todos los vecinos, y el modelo votante, que copia la dirección de un único
vecino elegido al azar.

Los parámetros fijados por la cátedra son `L=10`, `rc=1`, `dt=1` y `v=0.03`.
Las densidades principales son `rho=2,4,8`, equivalentes a `N=200,400,800`.

## Estado actual

La especificación base de la Etapa 1 está documentada, aunque su cierre formal
sigue pendiente porque todavía falta congelar el formato de salida y el
protocolo experimental. La Etapa 2 se encuentra en progreso. Además de
la búsqueda de vecinos por fuerza bruta (oráculo de referencia) y el Cell
Index Method (CIM, el algoritmo eficiente de búsqueda de vecinos), ya están
implementadas y validadas las dos reglas de orientación (Vicsek y votante),
el paso temporal completo que las conecta con el movimiento de las
partículas (respetando la sincronía y el borde periódico), los dos
observables principales del TP (la polarización `va` y la fracción `S` del
cluster más grande) y un bucle reutilizable que encadena muchos pasos de
simulación, derivando una semilla distinta por paso. Todavía faltan la
escritura de texto y la CLI.

La Etapa 3 también está abierta: ya tiene validadas varias piezas puntuales,
incluida la reproducibilidad de la iteración en memoria, pero todavía faltan
los vecinos medios compatibles con la teoría, la salida reproducible a disco
y las validaciones de corridas largas (por ejemplo, el consenso del votante).

### Resumen de avance

Implementado y validado en memoria:

- estado, parámetros y geometría periódica;
- búsqueda de vecinos por fuerza bruta y Cell Index Method;
- reglas de Vicsek y votante;
- paso temporal sincrónico con movimiento backward;
- bucle de simulación con observador y semillas dependientes del paso;
- polarización `va` y componente conexa más grande `S`.

Todavía no implementado o no validado experimentalmente:

- salida de texto y CLI;
- series temporales persistidas de `va(t)` y `S(t)`;
- promedios estacionarios, `t_eq`, realizaciones y barras de error;
- pilotos, barridos, figuras y animaciones;
- benchmark contra TP1 y entregables finales.

La suite actual contiene siete tests y debe seguir pasando completa después de
cada cambio del motor.

## Criterio de interpretación

Una funcionalidad se considera implementada en este informe cuando existe
código y un test reproducible que la verifica. Esto no equivale a tener lista
la simulación experimental: todavía falta guardar series `va(t)` y `S(t)` a
disco, elegir el estacionario y repetir las corridas con un protocolo
estadístico.

## Implementación realizada

### Estado y parámetros

En `src/core/model.hpp` se definieron:

- `Parameters`, con los valores físicos comunes del TP.
- `Particle`, con `id`, posición `(x,y)` y orientación `theta`.

### Geometría periódica

En `src/core/periodic_geometry.hpp` se implementaron y probaron:

- repliegue periódico de coordenadas mediante `periodic_wrap`;
- distancia mínima entre partículas mediante `minimum_image_delta`;
- distancia al cuadrado con periodicidad;
- criterio de vecindad periódico.

### Vecinos por fuerza bruta

En `src/core/neighbor_search.hpp`, `brute_force_neighbors` recorre todos los
pares `i<j`, por lo que tiene complejidad `O(N^2)`. Para cada par:

1. calcula la distancia mínima periódica;
2. compara `d^2` contra `rc^2`, sin calcular raíces cuadradas;
3. si el par es vecino, agrega ambos IDs en las listas correspondientes.

La función no incluye auto-vecinos, usa el criterio inclusivo `d <= rc`, genera
listas simétricas y no produce duplicados. Las listas quedan ordenadas por ID,
lo que facilita compararlas con la implementación del CIM. El resultado
se indexa por posición en el vector de entrada y supone que los IDs son únicos.

## Verificación realizada

Se agregaron los tests de `tests/test_neighbor_search_bruteforce.cpp`, que
cubren los casos solicitados: pares más cercanos, exactamente en `rc` y más
lejanos; cruce de bordes y esquinas; simetría; ausencia de auto-vecinos y
duplicados; construcción manual de una cadena de vecinos; y determinismo.

La verificación ejecutada fue:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Resultado: los dos tests registrados (`periodic_geometry` y
`neighbor_search_bruteforce`) pasan. No se ejecutaron barridos ni se generaron
datos pesados.

## Cell Index Method (CIM)

### Qué es, en lenguaje sencillo

Buscar vecinos "por fuerza bruta" significa comparar cada partícula contra
todas las demás, una por una: si hay `N` partículas, eso son del orden de
`N^2` comparaciones. Funciona, pero se vuelve lento cuando `N` crece (por
ejemplo con `N=800`).

El Cell Index Method evita comparar contra todo el mundo. La idea es simple:
se divide la caja en una grilla de celdas cuadradas, cada partícula se
"archiva" en la celda donde cae según su posición, y para buscar los vecinos
de una partícula alcanza con mirar las partículas archivadas en su propia
celda y en las 8 celdas que la rodean. Como el radio de interacción `rc` es
chico frente a la caja, ninguna partícula fuera de esas celdas puede estar a
distancia `rc` o menos: no hace falta revisarla. Así se ahorra la mayoría de
las comparaciones sin dejar de detectar ningún par vecino.

Para que este atajo sea seguro, el tamaño de cada celda tiene que ser al
menos `rc`. Con `L=10` y `rc=1` (los valores del TP), la grilla queda de
`10x10` celdas de lado `1.0` exactamente. El borde periódico de la caja se
respeta dos veces: al decidir en qué celda cae cada partícula (una partícula
muy cerca de `x=0` "sabe" que también es vecina de la zona cercana a
`x=L`), y al mirar las celdas alrededor de cada celda (la última columna de
celdas tiene como vecina a la primera, no queda afuera).

### Cómo se compara con la fuerza bruta

`brute_force_neighbors` (ya implementada en una tarea anterior) sirve como
"respuesta correcta" de referencia: es lenta pero fácil de convencerse de que
es correcta, porque compara literalmente todos los pares. La nueva función
`cell_index_neighbors` tiene que producir, partícula por partícula, la misma
lista de vecinos (mismos IDs, mismo orden tras ordenar) que la fuerza bruta,
para cualquier configuración de partículas. El test no se conforma con que
ambas den la misma *cantidad* de vecinos: compara las listas completas de
IDs, y si alguna partícula difiere, el test falla imprimiendo cuál partícula
es, en qué posición del vector de entrada estaba, y las dos listas completas
(fuerza bruta y CIM) para poder diagnosticar el error de inmediato.

### Qué casos se validaron

El archivo `tests/test_neighbor_search_cim.cpp` compara ambos métodos en 13
situaciones distintas:

1. Muchos estados chicos (`N=12`) generados con 30 semillas fijas distintas.
2. Estados aleatorios uniformes de tamaño moderado (`N=120`), varias semillas.
3. Partículas que cruzan el borde periódico en `x`.
4. Partículas que cruzan el borde periódico en `y`.
5. Partículas que cruzan una esquina periódica.
6. Pares separados exactamente por `rc` (el borde debe contar como vecino).
7. Pares separados apenas más que `rc` (no deben ser vecinos).
8. Varias partículas conviviendo en la misma celda de la grilla.
9. Partículas repartidas en celdas vecinas (horizontal, vertical y diagonal).
10. Partículas en celdas lejanas, que no deben tener ningún vecino.
11. Simetría, ausencia de auto-vecinos y ausencia de duplicados, revisadas
    directamente sobre la salida del CIM.
12. Independencia del orden de almacenamiento: se calculan los vecinos con
    las partículas en un orden, se mezcla ese orden y se vuelve a calcular;
    la lista de vecinos de cada partícula (identificada por su `id`, no por
    su posición) debe ser idéntica en ambos casos.
13. Varios tamaños de sistema, incluyendo casos límite: `N` desde 0 hasta 50.

### Qué resultado se obtuvo

Los 13 casos pasaron sin diferencias entre el CIM y la fuerza bruta. La
suite completa de tests (`periodic_geometry`, `neighbor_search_bruteforce`,
`neighbor_search_cim`) corre en verde:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Resultado: `100% tests passed, 0 tests failed out of 3`.

Con esto queda cerrado el punto "CIM contra fuerza bruta" de las
validaciones mínimas de la Etapa 3, aunque la Etapa 2 y la Etapa 3 siguen
abiertas en general porque faltan otras piezas del motor (ver "Pendientes y
decisiones abiertas" al final de este archivo).

## Reglas de orientación: Vicsek y votante

### Qué es, en lenguaje sencillo

Una vez que se sabe quiénes son los vecinos de cada partícula (con fuerza
bruta o con el CIM), falta decidir cómo cada partícula elige su nueva
dirección de movimiento a partir de esos vecinos. El TP compara dos formas
distintas de decidir eso:

- **Vicsek**: cada partícula le pregunta a todos sus vecinos (y también se
  tiene en cuenta a sí misma) hacia dónde apuntan, y calcula una dirección
  promedio. Es una regla "democrática": todos opinan y se saca un promedio.
- **Votante**: cada partícula elige un único vecino al azar y copia
  exactamente su dirección, sin promediar con nadie más. Es una regla de
  "imitación": no hay promedio, hay copia de una sola fuente. Si no tiene
  ningún vecino, se queda con su propia dirección.

En los dos casos se agrega después un poco de ruido al azar, para que el
movimiento no sea perfectamente determinista.

En la implementación, `eta <= 0` se trata como ausencia de ruido. Para el TP
se usarán valores no negativos de `eta`; esta convención solo evita un
comportamiento ambiguo en casos de test o entradas inválidas.

Un detalle técnico importante de Vicsek: promediar ángulos directamente
(sumar los números y dividir por la cantidad) da resultados absurdos cerca
de `0°`/`360°`. Por ejemplo, promediar `1°` y `359°` "a mano" da `180°`, que
es exactamente la dirección opuesta a la correcta (el promedio real de esas
dos direcciones, que están casi pegadas, es `0°`). Para evitar ese error se
usa una fórmula distinta (`atan2` sobre la suma de senos y cosenos) que sí
calcula el promedio geométrico correcto de un conjunto de direcciones.

### Ejemplo sencillo

- Vicsek: si una partícula mira hacia el este y sus dos vecinos miran hacia
  el norte y hacia el sur, la partícula termina mirando aproximadamente
  hacia el este (el promedio de las tres direcciones), más un poco de
  ruido.
- Votante: en la misma situación, la partícula elige al azar a uno de los
  dos vecinos externos y copia esa dirección exacta, más el mismo tipo de
  ruido. No hay ningún promedio de por medio y la propia partícula no puede
  ser elegida.

### Qué se implementó y cómo se validó

En `src/core/rules.hpp` se agregaron `vicsek_update` y `voter_update`.
Ninguna de las dos funciones modifica las orientaciones viejas: ambas leen
el estado anterior y devuelven un vector nuevo con las orientaciones
calculadas, lo que permite actualizar a todas las partículas "al mismo
tiempo" (sincronía), sin que el resultado dependa del orden en que se
procesan.

Los tests de `tests/test_rules.cpp` (registrados en CTest como `rules`)
verifican, entre otras cosas:

- que una partícula aislada sin ruido se queda con su propia dirección, en
  ambas reglas;
- que Vicsek promedia bien incluso cuando las direcciones están cerca de
  `0°`/`360°` (el caso `1°`/`359°` mencionado arriba, y otro caso similar
  con `350°`/`10°`);
- que Vicsek da el resultado numérico exacto esperado para un ejemplo
  armado a mano (tres partículas con direcciones conocidas);
- que votante, sin ruido, siempre termina copiando exactamente la dirección
  de algún vecino (nunca inventa una dirección intermedia) y nunca se elige
  a sí misma;
- que con ruido, el cambio en votante queda acotado al rango de ruido
  permitido;
- que el resultado es reproducible si se usa la misma semilla del
  generador aleatorio, y que semillas distintas pueden dar resultados
  distintos.

### Qué resultado se obtuvo

Los 13 casos pedidos para esta tarea pasaron. La suite completa de tests
(`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`,
`rules`) corre en verde:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Resultado: `100% tests passed, 0 tests failed out of 4`.

Con esto se completa, dentro de la Etapa 3, el punto "Vicsek y votante
satisfacen reglas distintas", pero solo para el cálculo de la orientación a
partir de una lista de vecinos fija: todavía no existe el paso temporal
completo que combine esta regla con el movimiento de las partículas paso a
paso (ver "Pendientes y decisiones abiertas" al final de este archivo). La
Etapa 2 y la Etapa 3 siguen abiertas en general.

## Paso temporal completo (sincronía y movimiento backward)

### Qué es, en lenguaje sencillo

Ya sabíamos cómo encontrar vecinos y cómo cada partícula decide su nueva
dirección (Vicsek o votante). Faltaba la última pieza: cómo avanza el
sistema un instante de tiempo. Eso implica dos cosas que tienen que pasar
"al mismo tiempo, con las reglas del instante viejo":

1. Cada partícula calcula su nueva dirección mirando solamente cómo estaban
   las cosas *antes* de este paso (nunca mirando direcciones que otras
   partículas ya recalcularon en este mismo paso).
2. Cada partícula se mueve un poquito (`v * dt`) en la dirección en la que
   estaba mirando *antes* del paso, no en la dirección nueva recién
   calculada. Esa dirección nueva recién se usará para moverse en el
   próximo paso. A esto se lo llama movimiento "backward": la orientación
   "llega" un paso después que el movimiento.

Un ejemplo para entenderlo: una partícula está en el origen mirando hacia el
este (ángulo `0`), y sus vecinos hacen que su nueva dirección "deseada" sea
hacia el norte (`pi/2`). En este paso, la partícula todavía se mueve hacia
el este (la dirección vieja); recién en el paso siguiente, ya mirando hacia
el norte, empezará a moverse hacia el norte.

Después de mover a todas las partículas, se aplica el borde periódico: si
alguna se sale de la caja por un lado, reaparece del otro.

### Qué se implementó y cómo se validó

En `src/core/time_step.hpp` se agregó `advance_time_step`, que junta en el
orden correcto la búsqueda de vecinos, las reglas de orientación y el
movimiento, sin repetir código de ninguna de esas tres partes (reutiliza
`neighbor_search.hpp` y `rules.hpp` tal cual estaban). No modifica el
estado viejo: siempre devuelve un estado nuevo completo.

Los tests de `tests/test_time_step.cpp` (registrados en CTest como
`time_step`) verifican, entre otras cosas, el caso mínimo que exige la
consigna: una partícula en `(0,0)` mirando al este (`theta=0`), con una
interacción que fuerza su dirección nueva a `pi/2` (norte); con
`v=0.03,dt=1`, el resultado tiene que ser exactamente `x=0.03, y=0,
theta=pi/2`. Si el motor usara por error la dirección nueva para moverse,
el resultado sería `(0, 0.03)` en cambio — el test comprueba explícitamente
que eso NO ocurre.

También se verificó: el borde periódico se aplica bien a las posiciones
nuevas; los vecinos de cada paso se calculan con las posiciones de *antes*
de mover (no con las de después); el resultado no depende del orden en que
están guardadas las partículas en memoria (usando la misma semilla);
llamar dos veces con la misma semilla da el mismo resultado exacto; una
semilla distinta puede dar un resultado distinto; el paso da el mismo
resultado si se buscan los vecinos por fuerza bruta o por CIM; y que
encadenar dos pasos seguidos usa correctamente, en el segundo paso, la
posición ya actualizada por el primero.

### Un ajuste importante que salió de este trabajo

Al armar el test de "no importa el orden en que estén guardadas las
partículas", se descubrió un problema real en el diseño anterior de las
reglas de orientación: usaban un único generador de números aleatorios que
se consumía en el orden en que aparecían las partículas en la lista. Eso
significa que, si dos corridas usaban exactamente la misma semilla pero
guardaban a las mismas partículas en distinto orden, una misma partícula
(identificada por su `id`) podía terminar con un resultado distinto según
dónde había quedado guardada, no según quién era. Esto violaba un
requisito explícito de reproducibilidad del TP.

La solución fue hacer que cada partícula use su propio generador de
números aleatorios, derivado de la semilla general y de su propio `id`
(nunca de su posición en la lista). Así, el resultado de una partícula
depende únicamente de la semilla, de su identidad y de sus vecinos, nunca
de cómo esté ordenada la lista. Se agregó un test nuevo específico para
esto (además del que lo hizo evidente en el paso temporal).

### Qué resultado se obtuvo

Los 13 casos pedidos para el paso temporal pasaron, igual que un caso
adicional de invarianza al orden que se sumó a los tests de las reglas de
orientación (que ahora tienen 14 en vez de 13). La suite completa de tests
(`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`,
`rules`, `time_step`) corre en verde:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Resultado: `100% tests passed, 0 tests failed out of 5`.

Con esto se completa, dentro de la Etapa 3, el punto "Sincronía y
movimiento backward". La Etapa 2 y la Etapa 3 siguen abiertas en general:
en ese momento todavía faltaban los observables, los clusters, la salida de
texto y la CLI. Los dos primeros se documentan en la sección siguiente; la
salida de texto y la CLI siguen pendientes.

## Observables: polarización y cluster más grande

### Qué es, en lenguaje sencillo

Con el paso temporal ya funcionando, hacen falta números que resuman qué tan
"ordenada" está la bandada en un instante dado. El TP pide dos:

- **Polarización `va`**: mide cuánto apuntan las partículas en una dirección
  común. Se calcula sumando vectorialmente todas las direcciones (como
  flechas) y viendo qué tan larga queda la flecha resultante en relación a
  la cantidad de partículas. Si todas apuntan igual, la suma da una flecha
  larga: `va` cercano a 1 (bandada alineada). Si las direcciones se
  cancelan entre sí, la suma da una flecha corta o nula: `va` cercano a 0
  (direcciones que se cancelan, no hay orden colectivo).
- **Fracción `S` del cluster más grande**: mide qué proporción de partículas
  pertenece al grupo conectado más grande. Un cluster se arma por
  conexiones entre vecinos (si dos partículas están a distancia `rc` o
  menos, están conectadas), y esas conexiones pueden encadenarse: si A está
  conectada con B y B con C, las tres partículas forman un mismo cluster
  aunque A y C no sean vecinas directas entre sí. `S` es simplemente el
  tamaño del cluster más grande dividido por el total de partículas.

### Ejemplos simples

- Cuatro flechas apuntando exactamente igual: `va=1` (alineación perfecta).
- Dos flechas opuestas (una hacia el este, otra hacia el oeste): `va=0` (se
  cancelan por completo).
- Tres partículas conectadas en cadena, A con B y B con C, sin que A y C
  sean vecinas directas: igual forman un único cluster de tamaño 3, así que
  `S=1` para ese sistema (todas están en el mismo grupo, por transitividad).
- Dos grupos separados: por ejemplo, un grupo de 3 partículas conectadas
  entre sí y otro grupo de 2 conectadas entre sí, sin ningún vecino en
  común entre ambos grupos, sobre un total de 5. El cluster más grande es
  el de 3, así que `S=3/5`.

### Qué se implementó y cómo se validó

En `src/core/observables.hpp` se agregaron `polarization` (recibe el estado
de partículas y devuelve `va`) y `largest_cluster_size`/
`largest_cluster_fraction` (reciben las listas de vecinos ya calculadas —
por fuerza bruta o por CIM, da lo mismo — y el estado de partículas, y
devuelven el tamaño del cluster más grande o la fracción `S`). Ninguna de
las tres funciones modifica el estado ni las listas de vecinos que recibe.

Para encontrar los clusters se usa un algoritmo llamado **union-find**: cada
partícula arranca en su propio grupo, y por cada par de vecinos se van
"fusionando" los grupos a los que pertenecen. Al final, se cuenta cuántas
partículas quedaron en el grupo más grande. Se eligió por sobre recorrer el
grafo con una búsqueda en profundidad/anchura porque encaja mejor con la
forma en que ya vienen los datos (una lista de conexiones, no un grafo
pensado para recorrer nodo por nodo), y es más simple de leer.

Un detalle importante: las listas de vecinos identifican a cada partícula
por su `id`, no por la posición en la que está guardada en el vector (los
`id` ni siquiera tienen que ser consecutivos). El código arma primero un
mapa de `id` a posición antes de fusionar grupos, para no confundir nunca a
una partícula con otra.

**Convención cuando no hay partículas (`N=0`)**: se documentó explícitamente
que `va=0` y `S=0` en ese caso, en vez de dejar un comportamiento indefinido
o un error de división por cero.

Los tests de `tests/test_observables.cpp` (registrados en CTest como
`observables`) verifican, entre otras cosas:

- que una sola partícula o todas las partículas con la misma dirección dan
  `va=1`;
- que direcciones opuestas o balanceadas en cuatro direcciones distintas dan
  `va=0`;
- un caso con resultado numérico exacto conocido de antemano (`va=sqrt(2)/2`
  para dos partículas mirando al este y al norte);
- que un estado con direcciones al azar siempre da un `va` entre 0 y 1;
- que ninguna de las dos funciones modifica el estado que recibe;
- que la cadena A-B-C (donde A y C no son vecinas directas) forma un único
  cluster de tamaño 3, probando explícitamente la transitividad y no solo
  contando vecinos directos;
- que partículas conectadas cruzando el borde de la caja (una cerca de
  `x=0` y otra cerca de `x=L`) quedan en el mismo cluster, usando vecinos
  calculados con el CIM;
- que el cluster más grande da el mismo resultado usando fuerza bruta o CIM;
- que el algoritmo usa correctamente el `id` de cada partícula aunque los
  IDs no sean consecutivos (por ejemplo `7, 20, 99`).

### Qué resultado se obtuvo

Los 18 casos pedidos para esta tarea (8 de polarización, 10 de clusters)
pasaron. La suite completa de tests (`periodic_geometry`,
`neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`,
`observables`) corre en verde:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Resultado: `100% tests passed, 0 tests failed out of 6`.

Con esto se completa, dentro de la Etapa 3, el punto "`va` y `S` dentro de
límites y casos manuales correctos". La Etapa 2 y la Etapa 3 siguen abiertas
en general: todavía falta el bucle completo de simulación, la salida de
texto y la CLI (ver "Pendientes y decisiones abiertas" al final de este
archivo).

## Bucle de simulación y semillas por paso

### Qué es, en lenguaje sencillo

Hasta ahora se sabía cómo dar *un* paso de simulación: buscar vecinos,
decidir la nueva dirección de cada partícula y moverlas, todo de forma
sincrónica. Una simulación de verdad no es un solo paso: es repetir ese
mismo paso muchas veces, una tras otra. Cada paso nuevo tiene que partir del
estado que dejó el paso anterior (las posiciones y direcciones ya movidas),
nunca del estado original con el que arrancó todo.

Hay un detalle importante sobre el ruido al azar: si cada paso usara
exactamente la misma semilla aleatoria, se repetiría artificialmente el
mismo sorteo de ruido una y otra vez, como si el generador de números
aleatorios "no avanzara" entre pasos. Eso no es lo que se espera de una
simulación real: el ruido tiene que variar de un paso a otro. Por eso la
semilla que se usa para sortear el ruido de cada partícula tiene que
depender también de en qué paso está la simulación, no solo de la semilla
general de la corrida ni del `id` de la partícula.

### Qué se implementó y cómo se validó

En `src/core/simulation.hpp` se agregó `run_simulation`, que recibe el
estado inicial, la cantidad de pasos a ejecutar y una semilla base, y
devuelve el estado final después de ejecutar todos esos pasos. Internamente
no hace nada nuevo en cada paso: llama a `advance_time_step` (ya
implementado) una vez por paso, encadenando la salida de un paso como
entrada del siguiente.

Para resolver el problema de la semilla repetida, se agregó
`derive_step_seed(base_seed, step)`, que combina la semilla base y el
número de paso en una nueva semilla distinta para cada paso. Esa semilla de
paso se usa después exactamente igual que antes: se combina con el `id` de
cada partícula (esa parte ya existía, sin cambios). El resultado es que el
sorteo de ruido de una partícula en un paso dado depende de tres cosas: la
semilla general de la corrida, el número de paso, y el `id` de la
partícula — nunca de dónde está guardada esa partícula en la memoria.

También se agregó un "observador" opcional: una función que, si se provee,
se llama después de cada paso (y una vez al principio, con el estado
inicial) para poder mirar el estado en ese momento sin modificarlo. Por
ahora no hace nada con esa información (no calcula `va`/`S` ni escribe
nada), pero deja preparado el enganche para que, en una tarea futura, algo
externo a este bucle pueda ir registrando esos observables o escribiéndolos
a disco sin que el bucle de simulación tenga que saber nada de eso: cada
pieza sigue haciendo una sola cosa.

Los tests de `tests/test_simulation.cpp` (registrados en CTest como
`simulation`) verifican, entre otras cosas:

- que ejecutar cero pasos devuelve el estado inicial sin cambios;
- que ejecutar un paso da exactamente el mismo resultado que llamar una vez
  a `advance_time_step` con la semilla derivada del paso 1;
- que después de varios pasos se conservan la cantidad de partículas, sus
  `id`, y que las posiciones y direcciones siguen siendo válidas;
- que el observador recibe el estado correcto en cada paso, en el orden
  correcto, sin modificar el estado inicial;
- que la misma configuración y semilla base dan exactamente la misma
  corrida, y que una semilla distinta puede dar una corrida distinta;
- que el ruido de dos pasos consecutivos de la misma partícula no es
  idéntico (prueba directa de que la semilla efectivamente cambia entre
  pasos);
- que reordenar las partículas iniciales no cambia el resultado de cada una
  (identificada por `id`) después de varios pasos;
- que la corrida da el mismo resultado usando fuerza bruta o CIM para
  buscar vecinos;
- que una partícula aislada sin ruido conserva su dirección y se mueve
  según esa dirección en cada paso;
- que el segundo paso de una cadena usa las posiciones ya actualizadas por
  el primero (dos partículas que no eran vecinas al principio pasan a serlo
  recién después de moverse un paso).

### Qué resultado se obtuvo

Los 10 casos pedidos para esta tarea pasaron. La suite completa de tests
(`periodic_geometry`, `neighbor_search_bruteforce`, `neighbor_search_cim`,
`rules`, `time_step`, `observables`, `simulation`) corre en verde:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Resultado: `100% tests passed, 0 tests failed out of 7`.

Con esto se completa, dentro de la Etapa 3, el punto "bucle de simulación,
semillas por paso y reproducibilidad en memoria". Queda cubierta la
reproducibilidad de la iteración en memoria (mismo `base_seed`, misma
corrida); todavía falta la reproducibilidad de la salida a disco, que
depende de la escritura de texto (ver "Pendientes y decisiones abiertas" al
final de este archivo). Tampoco se congeló en esta tarea el formato de
salida ni la CLI.

## Revisiones técnicas acumuladas

La implementación revisada es correcta para el alcance de esta tarea. No se
detectaron errores en el algoritmo de fuerza bruta ni en los casos de prueba.
Se ajustó únicamente un comentario de `neighbor_search.hpp` para aclarar que
el resultado está indexado por posición, aunque las listas contienen IDs
estables. También se sincronizaron dos checks del plan con la evidencia ya
existente: la coincidencia CIM/fuerza bruta y la validación de la geometría.
Esto no cierra las etapas completas, porque todavía faltan otras piezas del
motor y validaciones.

La implementación de `polarization` y de los componentes conexos con
`union-find` también fue revisada y es correcta para el alcance declarado.
Los tests cubren los casos analíticos, la transitividad, el borde periódico,
IDs no consecutivos y las convenciones para `N=0`. Se agregó únicamente el
include explícito de `<utility>` en `observables.hpp`, requerido por
`std::swap`; no se modificó la lógica del algoritmo.

Queda registrado un riesgo para la siguiente integración: la semilla actual se
combina con el `id` de la partícula, pero `advance_time_step` todavía no recibe
el número de paso. El bucle que ejecute muchos pasos deberá derivar una semilla
distinta para cada par `(paso, id)` o incorporar explícitamente el tiempo en la
interfaz; de lo contrario, al reutilizar la misma semilla se repetirían los
mismos sorteos en cada paso.

## Próximos pasos

El siguiente desarrollo es la escritura de texto (formato de salida todavía
sin congelar) y la interfaz de ejecución (CLI), que van a apoyarse en el
observador de `run_simulation` para registrar `va(t)`/`S(t)` y/o la
trayectoria sin mezclar esa responsabilidad con el bucle de simulación.

## Pendientes y decisiones abiertas

- Falta la escritura de texto (salida a disco): el formato público de los
  archivos todavía es una decisión abierta y no se congeló en esta tarea.
- Falta la CLI.
- Falta el protocolo estadístico completo: promedio estacionario de los
  observables, elección de `t_eq`, realizaciones independientes y barras de
  error.
- Faltan las corridas largas (por ejemplo, para observar el consenso del
  votante sin ruido) y los pilotos que sirven para elegir la grilla de
  `eta` y la duración de las corridas.
- Faltan los barridos definitivos y las figuras.
- Siguen abiertas las decisiones experimentales sobre `eta`, duración,
  realizaciones, semillas, barras de error y formato final de salida.
- Falta verificar el número medio inicial de vecinos contra
  `rho*pi*rc^2` para `rho=2,4,8`.
- Falta decidir, antes del barrido de clusters, cómo convertir las densidades
  bajas `1/pi`, `1/(2*pi)` y `1/(3*pi)` a un número entero de partículas.
- Falta confirmar si esas densidades bajas también deben incluirse en el
  gráfico `<va>` vs. `<S>` del punto E, o solamente en el estudio de clusters
  del punto D.
- Falta definir el protocolo de benchmark contra TP1: tamaños, cantidad de
  pasos, realizaciones, entorno y tramo exacto que se cronometrará.
- Falta confirmar los datos administrativos, nombres de archivos y enlaces
  requeridos para la entrega.
- Falta confirmar las indicaciones visuales que no aparecen explícitamente en
  la guía escrita, como el tratamiento de grillas y la separación visual de
  `va` y `S`.
- No se pueden iniciar todavía los barridos definitivos ni las figuras.
