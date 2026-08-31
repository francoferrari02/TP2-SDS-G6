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
sigue pendiente porque todavía falta congelar el protocolo experimental (el
formato de salida sí quedó congelado e implementado en esta tarea). La Etapa 2
se encuentra en progreso. Además de la búsqueda de vecinos por fuerza bruta
(oráculo de referencia) y el Cell Index Method (CIM, el algoritmo eficiente de
búsqueda de vecinos), ya están implementadas y validadas las dos reglas de
orientación (Vicsek y votante), el paso temporal completo que las conecta con
el movimiento de las partículas (respetando la sincronía y el borde
periódico), los dos observables principales del TP (la polarización `va` y la
fracción `S` del cluster más grande), un bucle reutilizable que encadena
muchos pasos de simulación derivando una semilla distinta por paso, y ahora
también el escritor de salida (`observables.csv`/`trajectory.csv`) y una CLI
productiva (`simulate`) que lo conecta todo. Todavía falta decidir el
protocolo estadístico que se va a correr con esa CLI.

La Etapa 3 también está abierta: ya tiene validadas varias piezas puntuales,
incluidas la reproducibilidad de la iteración en memoria, el número medio
inicial de vecinos compatible con la teoría (ahora generado con el
inicializador productivo del estado, en vez de una función propia del
test), evidencia diagnóstica de que el votante sin ruido alcanza consenso
exacto en un escenario controlado (grafo completo, `N=20`, 10 semillas), y la
reproducibilidad/lectura independiente de los archivos de salida. Todavía
falta la validación de consenso con los parámetros físicos completos del TP.

### Resumen de avance

Implementado y validado en memoria:

- estado, parámetros y geometría periódica;
- búsqueda de vecinos por fuerza bruta y Cell Index Method;
- reglas de Vicsek y votante;
- paso temporal sincrónico con movimiento backward;
- bucle de simulación con observador y semillas dependientes del paso;
- polarización `va` y componente conexa más grande `S`;
- número medio inicial de vecinos, comparado contra la predicción teórica
  `rho*pi*rc^2` para las tres densidades obligatorias;
- consenso exacto del votante sin ruido en un escenario diagnóstico
  controlado (grafo completo, no los parámetros físicos completos del TP);
- inicializador productivo del estado (posiciones y orientaciones uniformes,
  semilla explícita), reutilizado por la validación de vecinos medios y
  directamente compatible con el bucle de simulación;
- escritor de salida (`observables.csv`/`trajectory.csv`, dos archivos CSV
  autocontenidos por corrida) y CLI productiva (`simulate`), con directorio
  propio por corrida, trayectoria opcional, strides configurables y
  protección contra sobrescritura accidental.

Todavía no implementado o no validado experimentalmente:

- promedios estacionarios, `t_eq`, realizaciones y barras de error;
- valores productivos concretos de stride, grilla de `eta` y semillas;
- pilotos, barridos, figuras y animaciones;
- benchmark contra TP1 y entregables finales.

La suite actual contiene once tests (`periodic_geometry`,
`neighbor_search_bruteforce`, `neighbor_search_cim`, `rules`, `time_step`,
`observables`, `simulation`, `mean_neighbors`, `initialization`,
`text_output`, `cli_simulate`) y debe seguir pasando completa después de cada
cambio del motor.

## Criterio de interpretación

Una funcionalidad se considera implementada en este informe cuando existe
código y un test reproducible que la verifica. Esto no equivale a tener lista
la simulación experimental: aunque ya se pueden guardar series `va(t)` y
`S(t)` a disco con la CLI, todavía falta elegir el estacionario y repetir las
corridas con un protocolo estadístico completo.

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
movimiento backward". Esta sección conserva el estado histórico de esa
tarea: en ese momento todavía faltaban los observables, los clusters, la
salida de texto y la CLI. Esas piezas se implementaron posteriormente y su
estado actual se resume en las secciones correspondientes de este informe.

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
límites y casos manuales correctos". Esta sección describe el estado de la
tarea cuando se implementaron los observables; posteriormente se agregaron
el bucle completo de simulación, la salida de texto y la CLI. Ver sus
secciones específicas y el resumen final para conocer el estado vigente.

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
semillas por paso y reproducibilidad en memoria". Esta sección registra el
estado de esa tarea antes de implementar la salida a disco; posteriormente
se congeló e implementó el formato de salida y la CLI, cuya evidencia figura
en la sección "Escritor de salida y CLI".

## Validación del número medio de vecinos

Cada partícula busca sus vecinos dentro de un círculo de radio `rc`
alrededor de su posición (sin contarse a sí misma). Si las posiciones son
uniformes en la caja, el número esperado de vecinos que caen dentro de ese
círculo depende de dos cosas: cuántas partículas hay por unidad de área
(la densidad `rho`) y cuán grande es el círculo (su área, `pi*rc^2`). Por
eso el valor esperado es el producto `rho*pi*rc^2`: a mayor densidad, más
partículas caen dentro del mismo círculo, así que el número medio de
vecinos debe crecer con `rho`.

Este resultado es una propiedad estadística, no una igualdad exacta: una
única inicialización fluctúa alrededor del valor teórico simplemente por
azar (algunas partículas caen cerca de otras, otras quedan más aisladas).
Por eso la validación promedia muchas inicializaciones independientes
(realizaciones), en vez de confiar en una sola.

Se implementó `tests/test_mean_neighbors.cpp` (registrado en CTest como
`mean_neighbors`), que genera posiciones uniformes iniciales con semillas
explícitas para las tres densidades obligatorias del TP y mide el promedio
de vecinos externos usando el Cell Index Method (CIM), sin modificar el
algoritmo de vecinos ni el motor. Para cada densidad se promedian 40
realizaciones independientes.

Hay dos formas válidas de expresar el valor esperado, y conviene no
confundirlas. La que usa la cátedra es la aproximación asintótica
`rho*pi*rc^2 = (N/L^2)*pi*rc^2`. Pero, en rigor, para una caja periódica
(sin efecto de borde) la cuenta exacta de vecinos *externos* (sin contar a
la propia partícula) tiene un valor esperado ligeramente distinto:
`(N-1)*pi*rc^2/L^2`, porque cada una de las otras `N-1` partículas (no
`N`) es la que puede caer dentro del círculo. La diferencia entre ambas es
exactamente `pi*rc^2/L^2` (≈0.031 para `L=10`, `rc=1`), y se explica
enteramente porque una partícula nunca puede contarse a sí misma como
vecina.

| rho | N | aproximada `rho*pi*rc^2` | finita exacta `(N-1)*pi*rc^2/L^2` | medido |
|---:|---:|---:|---:|---:|
| 2 | 200 | 6.283 | 6.252 | 6.355 |
| 4 | 400 | 12.566 | 12.535 | 12.502 |
| 8 | 800 | 25.133 | 25.101 | 25.123 |

Los tres valores medidos caen cerca de ambas referencias, y se verifica
además que el promedio crece estrictamente con la densidad
(`mean_k(rho=2) < mean_k(rho=4) < mean_k(rho=8)`). El criterio de
aceptación del test no cambió: sigue comparando contra la aproximación de
la cátedra, con una tolerancia del 5% pensada para absorber tanto la
fluctuación estadística normal de 40 realizaciones como el corrimiento
sistemático (y ya explicado) hacia la expectativa finita exacta; un error
real de geometría, periodicidad, radio o asignación de vecinos produciría
desvíos mucho mayores o rompería el orden entre densidades. Detalle
completo (semillas, criterio de aceptación y justificación de la
tolerancia) en `plan_desarrollo_tp2/03_validaciones.md`.

Esta prueba valida únicamente la inicialización uniforme y la búsqueda de
vecinos en el estado inicial; no valida el comportamiento dinámico de la
simulación (no ejecuta ningún paso de `advance_time_step`).

## Inicialización reproducible del estado

### Cómo se distribuyen inicialmente las partículas

Al arrancar una simulación (o una validación que necesite un estado inicial),
cada partícula recibe una posición `(x,y)` dentro de la caja y una dirección
`theta`. La posición se sortea de manera **uniforme** dentro de la caja: cada
punto de la caja tiene la misma probabilidad de "recibir" una partícula, sin
favorecer ninguna zona. Esto es lo que corresponde a un gas de partículas sin
ninguna estructura previa: no hay ninguna razón física, en el instante
inicial, para que las partículas se agrupen en un lugar particular de la
caja.

### Por qué las orientaciones son aleatorias

La dirección inicial de cada partícula también se sortea uniforme, esta vez
sobre todo el círculo (`0` a `360` grados). La idea es la misma: al empezar,
no hay ninguna dirección preferida. Si se empezara con todas las partículas
mirando hacia el mismo lado, ya se estaría imponiendo artificialmente el tipo
de orden (alineación) que se supone que el sistema tiene que desarrollar (o
no) por sí mismo a medida que avanza la simulación.

### Qué significa usar una semilla

Los sorteos "al azar" de una computadora en realidad no son azarosos: se
calculan con una fórmula determinista que arranca de un número de partida
llamado semilla. Usar la misma semilla con la misma configuración vuelve a
producir, número por número, exactamente el mismo resultado; cambiar la
semilla cambia toda la secuencia de números generados. Esto es justamente lo
que permite reproducir una corrida (repetirla exactamente igual para
verificarla) y, al mismo tiempo, generar corridas distintas cuando hace falta
(por ejemplo, para tener varias realizaciones independientes). El
inicializador nunca usa el reloj de la computadora como semilla: la semilla
siempre la elige y controla quien llama, explícitamente.

### Por qué reutilizar el mismo inicializador

Antes de esta tarea, la validación del número medio de vecinos
(`tests/test_mean_neighbors.cpp`) tenía su propia función para generar
posiciones iniciales, separada de cualquier pieza que fuera a usar la
simulación real. Eso es un riesgo: si en algún momento esas dos formas de
generar el estado inicial dejaran de coincidir (por ejemplo, un rango
distinto, una distribución distinta, un orden distinto de sorteo), la
validación podría seguir "pasando en verde" sin que eso dijera nada real
sobre cómo arranca la simulación de verdad -- porque estaría validando una
inicialización distinta de la que efectivamente se usa.

Para evitar ese riesgo se creó un único inicializador productivo
(`src/core/initialization.hpp`, funciones `initialize_particles` e
`initialize_particles_from_density`) y se lo conectó en dos lugares: la
validación de vecinos medios ahora lo usa en vez de tener su propia función,
y el estado que devuelve se puede pasar directamente a `run_simulation` (el
bucle de simulación) sin ninguna adaptación. Así, tanto la validación como
una corrida real arrancan siempre de la misma forma de generar posiciones y
direcciones, con la misma semilla explícita y reproducible.

El inicializador usa `std::mt19937_64` (generador de 64 bits, no el
`std::mt19937` de 32 bits) para mantener consistencia con el resto del motor,
que ya trabaja con semillas de 64 bits en el bucle de simulación y en las
reglas de orientación.

Se agregó `tests/test_initialization.cpp` (11 casos) que verifica, entre
otras cosas: que los IDs sean consecutivos y únicos; que las posiciones
queden en `[0,L)` y las orientaciones en `[0,2*pi)`; que la misma semilla
reproduzca exactamente el mismo estado y que semillas distintas puedan dar
estados distintos; que las tres densidades obligatorias (`rho=2,4,8`)
produzcan `N=200,400,800`; que la inicialización no modifique los
parámetros; que funcione con `N=0`; que el estado generado se pueda usar
directamente con `run_simulation`; y que el resultado no dependa del reloj
de la computadora.

## Escritor de salida y CLI

Esta sección describía originalmente una **propuesta** de formato de salida.
Esa propuesta ya fue aprobada e **implementada**: existe un escritor de
archivos (`src/core/text_output.hpp`) y una interfaz de línea de comandos
productiva (`src/cli/simulate_cli.hpp`, `src/cli/simulate.cpp`, ejecutable
`simulate`). El detalle completo, con las alternativas comparadas y el
razonamiento de cada elección, además del registro formal de la decisión
aprobada, está en `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`.

En lenguaje simple, la idea implementada es: cada corrida (una combinación de
modelo, densidad, `eta`, semilla y número de realización) produce su propio
directorio con **dos** archivos de texto separados, nunca uno solo y nunca
mezclados con otra corrida:

- un archivo de **observables**, chico, con una línea por paso de tiempo:
  el paso `t`, la polarización `va(t)` y la fracción del cluster más grande
  `S(t)`. Esto es lo único que hace falta para las curvas de series
  temporales y para las curvas `<va>` vs. `eta`, `<S>` vs. `eta` y `<va>`
  vs. `<S>` que pide el enunciado;
- un archivo de **trayectoria**, potencialmente mucho más grande, con una
  línea por cada partícula en cada paso: el paso `t`, el `id` de la
  partícula, su posición `x,y` y su orientación `theta`. Esto es lo único
  que necesita el módulo de animación para dibujar el vector velocidad de
  cada partícula (no hace falta guardar `vx,vy` por separado, porque la
  velocidad se reconstruye a partir de `theta` y de la velocidad fija `v`,
  que queda registrada en el propio archivo).

El archivo de trayectoria es opcional: está desactivado por defecto, y se
activa explícitamente con `--write-trajectory` en la CLI, sin dejar de
escribir el archivo de observables. Así, un barrido grande con muchas
combinaciones y realizaciones puede evitar generar una cantidad enorme de
datos de trayectoria, y esa trayectoria completa se reserva solo para los
pocos casos elegidos para animar.

Ambos archivos empiezan con dieciocho líneas de comentario (con `#`) que
identifican de forma autocontenida qué corrida los produjo: modelo, `L`,
`rc`, `dt`, `v`, densidad nominal, `N`, densidad efectiva, `eta`, semilla
base, número de realización y más. Esto es justamente lo que garantiza que un
archivo, aislado, sea reproducible y legible sin depender de ningún otro
archivo ni de recordar cómo se llamó el programa que lo generó. El separador
es la coma (formato CSV), el más simple de leer sin ambigüedad tanto desde
Python (`pandas.read_csv`) como desde C++ o cualquier otra herramienta; el
separador decimal es siempre el punto, sin importar la configuración regional
de la computadora donde corra el motor.

Cada corrida escribe en su propio directorio, con una estructura que ya deja
diferenciados el modelo, la densidad, `eta`, la cantidad de pasos, el número
de realización y la semilla, por ejemplo:

```text
output/vicsek/rho_2/eta_0p5/steps_2000/realization_003_seed_12345/
  observables.csv
  trajectory.csv
```

Si ese directorio ya existe, la CLI se niega a escribir nada (ni siquiera lo
crea) salvo que se pida explícitamente `--overwrite`; con `--overwrite`, si la
corrida nueva no pide trayectoria, se elimina cualquier `trajectory.csv` viejo
para que no queden datos de una corrida anterior mezclados con los nuevos.
Los archivos se escriben primero con un nombre temporal y recién se renombran
al terminar, para no dejar nunca un archivo a medio escribir si algo falla en
el medio.

Se compararon brevemente tres alternativas para el formato de archivo: un
único archivo que mezclara observables y trayectoria (descartada por
desperdiciar espacio y mezclar dos tipos de fila muy distintos en el mismo
archivo), un archivo separado por cada paso de tiempo al estilo de algunos
simuladores de partículas (descartada como formato general porque,
multiplicada por todas las combinaciones y realizaciones del barrido,
generaría una cantidad de archivos difícil de manejar), y los dos archivos
por corrida descritos arriba, que fue la alternativa elegida.

Lo que todavía no está decidido es la **frecuencia productiva** de muestreo:
la CLI ya acepta un "stride" (cada cuántos pasos se guarda una fila) tanto
para observables como para trayectoria, y garantiza guardar siempre el primer
y el último paso aunque no sean múltiplos del stride, pero qué valores
concretos de stride se van a usar en el barrido definitivo sigue siendo una
decisión pendiente (ver "Pendientes y decisiones abiertas").

### Revisión de robustez (validación de entradas y publicación de archivos)

Después de implementar el escritor y la CLI, se hizo una revisión enfocada
en qué pasa con entradas raras o con fallas del sistema de archivos, sin
tocar el formato público ni agregar ninguna funcionalidad nueva. Se
corrigieron cuatro puntos:

1. **Valores numéricos sin sentido físico.** `--rho-nominal` y `--eta` ahora
   rechazan explícitamente `NaN`, `+infinito` y `-infinito` (antes solo se
   comprobaba el signo); `--rho-nominal` además tiene que ser estrictamente
   mayor que cero (antes se aceptaba cero o negativo).
2. **Nombres de densidad peligrosos.** `--rho-label` (la etiqueta que se usa
   tal cual como nombre de carpeta, por ejemplo `rho_2`) antes solo
   rechazaba espacios y barras; ahora solo acepta letras, números, `_` y
   `-`. Con esa restricción, valores como `.`, `..` o `../escape` quedan
   excluidos automáticamente, sin tener que pensar en cada caso raro por
   separado: si no está en la lista de caracteres permitidos, se rechaza.
3. **Colisión de nombres por redondeo.** El segmento `eta_...` del nombre de
   carpeta se arma redondeando `eta` a una cantidad de dígitos. Antes esa
   cantidad era fija (10 dígitos), lo que en teoría podía hacer que dos
   valores de `eta` distintos pero muy cercanos terminaran generando el
   mismo nombre de carpeta y se mezclaran sin darse cuenta. Ahora se usa la
   misma cantidad de dígitos que ya se usaba dentro de los archivos (17,
   suficiente para que cualquier número de punto flotante se pueda
   reconstruir exactamente), así que dos valores distintos de `eta` nunca
   producen el mismo nombre.
4. **Publicación de archivos más cuidadosa.** Antes, la CLI escribía el
   archivo temporal de observables y lo renombraba al nombre final, y recién
   después hacía lo mismo con la trayectoria. Eso significaba que, si la
   escritura de la trayectoria fallaba a mitad de camino, ya podía haber
   quedado publicado un `observables.csv` nuevo sin su `trajectory.csv`
   correspondiente. Ahora se escriben y verifican **los dos** archivos
   temporales completos primero (comprobando que se pudieron abrir, escribir
   y cerrar sin errores), y recién después se publican con el nombre final:
   primero la trayectoria, y `observables.csv` al final (porque
   `observables.csv` es, por contrato, la señal de que la corrida terminó
   bien). Si algo falla en cualquier paso, se borran los archivos temporales
   que se hayan llegado a crear y no se toca ningún archivo final. Si
   `--overwrite` tiene que borrar una trayectoria vieja porque la corrida
   nueva no pide trayectoria, ahora se comprueba que el borrado haya
   funcionado; si falla, se informa error en vez de seguir adelante como si
   nada.

**Límite real que queda documentado, no resuelto**: no existe en C++17
portable una forma de renombrar dos archivos como una única operación
atómica. Si el programa se interrumpiera exactamente entre publicar
`trajectory.csv` y publicar `observables.csv` (por ejemplo, un corte de luz
en ese instante preciso), el directorio podría quedar con una trayectoria
nueva pero sin `observables.csv` actualizado. La función nunca informa éxito
en ese caso, y la forma de recuperarse es simplemente volver a correr la
misma corrida con `--overwrite`.

## Pilotos y protocolo estadístico (propuesta preliminar)

Con el escritor de salida y la CLI ya validados, se ejecutó un primer lote de
corridas piloto: 108 corridas pequeñas (`2` modelos x `3` densidades
obligatorias x `6` valores exploratorios de `eta` x `3` realizaciones,
`steps=600`, CIM, sin trayectoria salvo una corrida de inspección puntual),
lanzadas y analizadas con dos herramientas nuevas de solo biblioteca
estándar de Python: `python/pilot_run.py` (lanza la grilla invocando el
binario `simulate` ya existente, con semillas explícitas y deterministas) y
`python/pilot_analyze.py` (relee cada `observables.csv` de forma
independiente, sin confiar en el lanzador, verifica el formato y agrega
tablas de resumen). El detalle completo -- grilla, comandos, tablas de
`<va>` por combinación, series temporales muestreadas y las propuestas
preliminares que surgen -- está en
`plan_desarrollo_tp2/05_pilotos_y_grilla_eta.md`, sección "Piloto ejecutado
(2026-08-30)".

En resumen, sin repetir aquí las tablas completas:

- Los 108 `observables.csv` generados pasaron la verificación independiente
  de formato (t ordenado, `va`/`S` en `[0,1]`, `t=0` y paso final presentes,
  metadatos completos): 108/108 válidos.
- `<va>` decrece monótonamente con `eta` en ambos modelos y las tres
  densidades, como espera la teoría; `S` se mantiene cerca de 1 en casi
  todos los casos con `rho=2,4,8` (estas densidades ya superan holgadamente
  el umbral de percolación de un disco de radio `rc=1`).
- Vicsek se estabiliza rápido (dentro de los primeros 100-200 pasos de los
  600 usados) para `eta<=2` en las tres densidades. El votante con `eta=0`,
  en cambio, **no** se estabiliza dentro de los 600 pasos usados en ninguna
  de las tres densidades: la serie sigue subiendo al final de la corrida, a
  diferencia de la regresión diagnóstica de grafo completo (ver sección
  "Regresión del votante sin ruido" más abajo), que alcanza consenso rápido
  solo porque asume conectividad total, no la densidad real del TP. Con el
  mismo protocolo para ambos modelos, esta es evidencia directa de que el
  votante necesita sustancialmente más pasos que Vicsek para relajar con los
  parámetros físicos reales.
- Con solo 3 realizaciones, el desvío entre ellas es grande cerca de la
  transición orden/desorden (por ejemplo `vicsek rho=2 eta=3`: `±0.18`,
  comparable al propio valor medio), lo que indica que 3 realizaciones no
  van a alcanzar para un error chico en esa zona del barrido definitivo.

Estos resultados son evidencia preliminar, no una grilla de `eta`, un `t_eq`,
una cantidad de realizaciones ni una definición de barras de error
definitivos: esas decisiones siguen abiertas en `DECISIONES_PENDIENTES.md`,
ahora con esta evidencia registrada junto a cada ítem. No se ejecutó el
barrido definitivo, no se generó ninguna figura final y no se pilotaron
todavía las densidades bajas (`1/pi,1/(2pi),1/(3pi)`, conversión a `N`
pendiente).

Los datos crudos de las 108 corridas quedan fuera de control de versiones
(`data/pilots/`, agregado a `.gitignore`, junto con `data/raw/` para la
futura producción); lo que se versiona son las tablas de resumen livianas
(`data/summary/pilot_grid_1_manifest.csv`,
`pilot_grid_1_by_realization.csv`, `pilot_grid_1_by_combo.csv`,
`pilot_grid_1_series_sampled.csv`) y las dos herramientas de
`python/`.

## Regresión del votante sin ruido

**Consenso polar** significa que, en algún momento, todas las partículas
del sistema terminan apuntando exactamente en la misma dirección. Con el
modelo votante, cada partícula copia la orientación de otra partícula (o
conserva la propia si no tiene vecinos) y le suma ruido. Cuando `eta=0`,
ese ruido desaparece por completo: la regla ya no puede *crear* una
orientación nueva, solo puede *copiar* una que ya existía. Esto significa
que, a lo largo de toda la corrida, el conjunto de orientaciones distintas
presentes en el sistema nunca puede crecer, solo achicarse. Si eso sigue
pasando el tiempo suficiente, en algún punto solo debería quedar una única
orientación: consenso exacto.

Para comprobar esto se implementó una herramienta de regresión,
`tests/voter_consensus_regression.cpp` (ejecutable `voter_consensus_regression`,
compilado con `cmake --build build`, pero **no** registrado como test
automático de CTest, ver más abajo por qué). La configuración elegida usa
un sistema pequeño (`N=20`) con una búsqueda de vecinos "completa": cada
partícula ve a todas las demás como vecinas, sin depender de la posición
ni del radio de interacción `rc`. Se eligió este escenario, en vez de
correr los parámetros físicos completos del TP con un horizonte largo,
para aislar exclusivamente la propiedad de convergencia de la regla de
votante en sí, sin mezclarla con la velocidad de difusión espacial del
sistema (que depende de `v=0.03` y `L=10`, y que el TP no pide demostrar
en esta prueba puntual).

Se probaron **10 semillas independientes** explícitas (`700001` a
`700010`), cada una con su propio estado inicial aleatorio, y un horizonte
de **3000 pasos** por corrida. El resultado: las **10 de 10** corridas
alcanzaron consenso exacto (una única orientación distinta en todo el
sistema), en un rango de 17 a 64 pasos, muy por debajo del horizonte
disponible. La polarización `va` inicial varió entre `0.089` y `0.334`
según la semilla, y en todos los casos terminó en `va=1.000000`.

Esto es consenso exacto de orientaciones, no solo una polarización cercana
a 1: la herramienta compara las orientaciones una por una por **igualdad
exacta de punto flotante** (sin ninguna tolerancia) y cuenta cuántos valores
distintos quedan, en vez de confiar únicamente en que `va` se acerque a 1 por
redondeo de punto flotante. La comparación exacta es correcta -- no una
simplificación arriesgada -- precisamente porque `eta=0` elimina toda fuente
de ruido: la regla del votante, en ese caso, nunca hace una cuenta que pueda
introducir un error de redondeo, solo copia un valor que ya existía. Si
alguna semilla no hubiera
alcanzado consenso dentro del horizonte, la herramienta lo iba a informar
igual, sin forzar ningún resultado ni modificar la regla de votante: solo
tiene un assert real sobre invariantes que sí serían un bug (por ejemplo,
que la cantidad de orientaciones distintas aumente, algo que la regla no
debería permitir nunca con `eta=0`). Por no depender de un resultado
garantizado en todas las configuraciones posibles, esta herramienta se
dejó fuera del pase/fallo automático de CTest y se ejecuta explícitamente.

Esta regresión demuestra que la regla de votante en sí converge cuando
todas las partículas pueden interactuar entre sí. No demuestra todavía que
el consenso se alcance con los parámetros físicos completos del TP (menor
conectividad, movimiento real), que sigue pendiente.

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

## Estudio dedicado del votante: grilla refinada, R=20, 3000 pasos

El equipo decidió enfocar el resto del trabajo únicamente en el modelo de
**votante** (Vicsek queda fuera del alcance que se está desarrollando en esta
línea). A partir de la evidencia del primer piloto (108 corridas, ver
sección anterior) se fijó un protocolo más exigente, con las siguientes
decisiones ya tomadas:

- **Grilla de `eta`**: se partió de la exploratoria `{0,1,2,3,4,6}` y se
  refinó dos veces con evidencia real, no a ciegas: primero densificando
  entre `eta=2` y `eta=4` (zona donde `<va>` caía más rápido en el piloto
  inicial), y después agregando puntos con paso `0.2` entre `eta=0` y
  `eta=1.5` (la caída es todavía más pronunciada ahí). La grilla final
  usada es:

  ```text
  eta = {0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6}
  ```

  (16 valores). Agregar resolución en la zona de caída rápida no es un
  estudio adicional ni cambia el modelo: es exactamente el procedimiento que
  pide `plan_desarrollo_tp2/05_pilotos_y_grilla_eta.md` ("si el cambio de
  los observables queda mal resuelto, agregar puntos en esa zona"). Se
  evitó expresamente cualquier análisis fuera de alcance (no se estimó un
  `eta_c` de transición, no se calculó susceptibilidad).
- **Duración**: `steps=3000` (en vez de los `600` del piloto exploratorio),
  porque ese piloto ya había mostrado que el votante con `eta` bajo no se
  estabiliza en 600 pasos.
- **Realizaciones**: `R=20`, elegido porque con `R=3` el desvío entre
  realizaciones cerca de la transición era `±0.18` (comparable al propio
  valor medio); con `R=20` el error estándar del peor caso quedó en el
  orden de `0.01-0.05`.
- **Densidades**: las tres obligatorias (`rho=2,4,8`) y, para el estudio de
  clusters (punto D), las tres densidades bajas del enunciado
  (`1/pi,1/(2pi),1/(3pi)`), convertidas a `N=32,16,11` con la decisión
  del 2026-08-30 de redondeo al entero más cercano ya documentada en
  `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md` (se registra también la densidad
  efectiva: `0.32, 0.16, 0.11`).

Herramientas nuevas (solo biblioteca estándar de Python, más `matplotlib`
para los gráficos diagnósticos): `python/voter_eta_study_run.py`,
`python/voter_eta_study_analyze.py`, `python/voter_eta_study_plot.py` (para
`rho=2,4,8`); `python/voter_lowrho_cluster_study_run.py` y el mismo
`voter_eta_study_analyze.py`/`voter_lowrho_cluster_study_plot.py` (para las
densidades bajas); `python/voter_eta_refine_run.py` (agrega los puntos
nuevos de `eta` a un directorio de piloto ya existente, con índices de
semilla que no colisionan con los ya usados, para no pisar corridas
anteriores). En total: 1020 corridas válidas por estudio (0 fallos en
ambos), datos crudos en `data/pilots/voter_eta_study_1/` y
`data/pilots/voter_lowrho_cluster_study_1/` (fuera de git), tablas resumen
en `data/summary/voter_eta_study_1_*.csv` y
`data/summary/voter_lowrho_cluster_study_1_*.csv`, gráficos diagnósticos en
`figures/voter_eta_study_1/*.png` y
`figures/voter_lowrho_cluster_study_1/*.png`.

### Por qué 3000 pasos alcanzan para las densidades bajas (no es una suposición)

Antes de fijar `steps=3000` para las densidades bajas se corrió también una
duración de `6000` pasos (`voter_lowrho_cluster_study_2`) para descartar que
el sistema siguiera en transitorio. Comparando `<va>` estacionario entre
ambas duraciones (`rho=1/pi`), la mayor diferencia fue `0.057` (en
`eta=0.5`, del orden del propio desvío entre realizaciones ahí); el resto
coincide hasta el 3er/4to decimal. Si el sistema hubiera seguido relajando
entre `t=3000` y `t=6000`, el valor medido a 6000 pasos se habría corrido
sistemáticamente respecto al de 3000; no lo hizo. Es evidencia directa de
que el régimen ya era estacionario a los 3000 pasos.

La heurística automática de `t_eq` (que exige que todos los puntos
muestreados posteriores queden a menos de `0.03` del promedio final) marcó
igualmente `sin_evidencia` en varias combinaciones de densidad baja, incluso
a 6000 pasos. La razón es de **tamaño finito**, no de falta de
equilibración: con `N=11,16,32`, cada partícula pesa una fracción grande del
sistema, y en el votante una sola actualización puede cambiar de golpe la
orientación de varias partículas a la vez. Esa fluctuación no se achica
agregando más pasos, y el error estándar del promedio entre 20 realizaciones
queda, en varios puntos, del mismo orden que la tolerancia fija de la
heurística: alcanza con que una sola fluctuación estadística la exceda para
que el criterio automático informe "no hay evidencia", aunque el promedio
real ya esté establecido. **Conclusión para el informe final**: para las
densidades bajas, `t_eq` no se justifica citando el número automático (fue
calibrado para la escala de ruido de `rho=2,4,8`, mucho menor); hay que
justificarlo por inspección visual de la serie completa, respaldada por la
comparación cuantitativa 3000 vs. 6000 pasos de arriba.

### Resultado físico del estudio de clusters con densidades bajas

`S` cae de forma monótona con `eta`, desde `~0.86-0.98` en `eta=0` hasta
`~0.17-0.22` en `eta=6`, muy por debajo de 1 en todo el barrido (a
diferencia de `rho=2,4,8`, donde `S` se mantiene siempre cerca de 1). Es
consistente con que estas densidades (`rho*pi*rc^2` del orden de `1, 0.5,
0.33` vecinos medios) están por debajo del umbral de percolación de un
disco de radio `rc=1`: la red de vecinos queda fragmentada en varios
clusters chicos en vez de formar una única componente gigante.

### Comparación entre densidades obligatorias (`rho=2,4,8`): conclusiones verificadas

A partir de `data/summary/voter_eta_study_1_by_combo.csv` (grilla completa
de 16 `eta`, `R=20`, `steps=3000`):

- **Entre `rho=2` y `rho=4`, el *ritmo* de relajación temporal es similar**:
  con `eta=0`, ambas densidades alcanzan consenso casi exacto (`va=1.000000`
  con error estándar `~1e-15`) dentro de la ventana de 3000 pasos, y el
  `t_eq` heurístico da un orden de magnitud comparable (`~1000` para
  `rho=4`, `~1150` para `rho=2`). Esta parte de la conclusión original
  queda confirmada. **Aclaración importante**: donde no coinciden es en el
  *valor* estacionario de `<va>` para el mismo `eta>0` — por ejemplo, en
  `eta=0.5`, `rho=2` da `va=0.417` y `rho=4` da `va=0.277` (rho=4 queda
  sistemáticamente más bajo). Así que "se manifiesta de la misma manera" es
  cierto para la *dinámica temporal* (cuánto tarda en asentarse), pero no
  para el *nivel* de polarización alcanzado, que sí depende de la densidad.
- **`rho=8` tarda más en alcanzar el equilibrio de la polarización**:
  confirmado. Con `eta=0`, `rho=8` da `t_eq≈1950` (vs. `~1000-1150` en
  `rho=2,4`) y, más importante, **no llega a consenso exacto** dentro de los
  3000 pasos: `va=0.987±0.010` en vez de `1.000000`. Esto es consistente con
  el piloto exploratorio anterior (steps=600), donde `rho=8` con `eta=0` ya
  se veía más lento que `rho=2,4`. Una posible explicación física a
  verificar: en el modelo de votante, el tiempo de consenso de una
  población bien mezclada suele escalar con el tamaño de la población `N`
  (no solo con la densidad); como `rho=8` implica `N=800` frente a
  `N=200/400`, el efecto observado podría deberse más al tamaño del sistema
  que a la densidad en sí. No se investigó esto a fondo todavía; queda como
  posible punto a mencionar en el informe, sin afirmarlo como demostrado.
- **Para `eta>1.5`, correr más pasos no mejora la resolución**: verificado,
  pero con un matiz de alcance. La comparación 3000 vs. 6000 pasos que
  respalda esto se hizo únicamente sobre las **densidades bajas**
  (`1/pi,1/(2pi),1/(3pi)`, ver sección anterior), no sobre `rho=2,4,8`
  directamente (no se corrió una prueba a 6000 pasos para las densidades
  obligatorias). Cualitativamente es razonable esperar el mismo
  comportamiento en `rho=2,4,8` -- para `eta>=2` el `t_eq` heurístico ya da
  `0` en las tres densidades altas (ver tabla de comparación arriba), es
  decir que la serie se estabiliza casi de inmediato -- pero no hay todavía
  una verificación directa a 6000 pasos para esas tres densidades que lo
  confirme con el mismo nivel de evidencia que para las densidades bajas.
  Conviene no presentar esta conclusión como validada para `rho=2,4,8` sin
  esa verificación adicional, si se la va a citar en el informe final con
  el mismo peso.

### Grilla fina entre `eta=0` y `eta=0.2`: el "empeoramiento" en `eta=0.2` era ruido estadístico

Al inspeccionar las series temporales de `eta=0.2` se notó un pico seguido de
una caída antes de asentarse (por ejemplo `rho=2` llegaba a `~0.80` hacia
`t≈1650` y bajaba después). Para confirmar si era un transitorio sin
terminar o solo ruido de muestreo, se corrió una grilla fina dedicada
(`eta={0,0.05,0.1,0.15,0.2}`, mismas `rho=2,4,8`, `R=20`, pero
`steps=5000`): 300 corridas, 0 fallos. Herramientas:
`python/voter_eta_fine_lowrange_run.py` / `voter_eta_fine_lowrange_plot.py`.
Resultados en `data/summary/voter_eta_fine_lowrange_1_*.csv` y
`figures/voter_eta_fine_lowrange_1/*.png`.

La caída de `<va>` en esa zona es suave y monótona (sin saltos): de `1.0` en
`eta=0` a `0.72/0.65/0.52` en `eta=0.2` para `rho=2/4/8` respectivamente. Y
comparando `<va>` en `eta=0.2` entre la corrida de 3000 pasos y esta de 5000
pasos (semillas independientes), los valores coinciden dentro del margen de
error (`0.708` vs `0.723` en `rho=2`, `0.663` vs `0.650` en `rho=4`, `0.514`
vs `0.517` en `rho=8`), y la nueva serie no repite el pico-y-caída tan
marcado de la corrida anterior. Conclusión: ese patrón era mayormente
fluctuación estadística de una muestra de 20 realizaciones en una zona donde
orden y ruido compiten de forma pareja, no un transitorio sin terminar; el
valor de equilibrio ya estaba bien capturado a los 3000 pasos. Detalle
completo en `plan_desarrollo_tp2/05_pilotos_y_grilla_eta.md`.

### Definición de barras de error y de `t_eq`

Con los estudios anteriores ya ejecutados, se cerraron dos decisiones del
protocolo estadístico (`plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`,
sección "Decisiones resueltas"):

- **Barra de error**: se usa **error estándar** de la media entre
  realizaciones (`s/√R`, no el desvío entre realizaciones), en todas las
  figuras y para ambos observables (`va`, `S`). El desvío mide variabilidad
  real entre corridas y no se achica con `R`; el error estándar mide qué tan
  bien determinado está el promedio reportado y sí se achica con `R` (en
  este caso, `√20≈4.47` veces menor que el desvío), que es lo que interesa
  comunicar en una curva `⟨va⟩` vs. `eta`. Ambas cantidades quedan
  igualmente calculadas y disponibles en las tablas `*_by_combo.csv` de
  `data/summary/`.
- **`t_eq=1500`** (la segunda mitad de los 3000 pasos usados en todo el
  estudio del votante), como ventana estacionaria única para todas las
  combinaciones de densidad y `eta`.

**Gráficos que respaldan la elección de `t_eq=1500`, con su comparativa**:

- `figures/voter_eta_study_1/va_t_rho_2.png`, `va_t_rho_4.png`,
  `va_t_rho_8.png` (series `va(t)` para varios `eta` representativos, por
  densidad): en las tres, la mayoría de las curvas ya alcanzaron su nivel
  estacionario bien antes de `t=1500` (`eta=0` se estabiliza entre
  `t≈650-1200` según la densidad; `eta≥1.5` se estabiliza casi de
  inmediato, dentro de los primeros cientos de pasos). Los casos más lentos
  observados (`eta` cercano a la zona de transición, `~0.5-1`) siguen
  fluctuando con amplitud considerable incluso después de `t=1500`, pero
  alrededor de un nivel medio ya estable, no con una tendencia sistemática
  de subida o bajada -- es la comparativa cuantitativa de la sección
  anterior (`eta=0.2` a 3000 vs. 5000 pasos, valores coincidentes dentro del
  margen de error) la que confirma que ese nivel medio ya es el real, no un
  transitorio a mitad de camino.
- `figures/voter_lowrho_cluster_study_1/va_t_rho_1_over_pi.png` (y análogos
  para `rho_1_over_2pi`/`rho_1_over_3pi`): mismo patrón para las densidades
  bajas, respaldado además por la comparativa 3000 vs. 6000 pasos de la
  sección "Por qué 3000 pasos alcanzan para las densidades bajas" (arriba),
  que mostró que duplicar la duración no desplazó el valor medio de `⟨va⟩`
  en ningún `eta`.
- `figures/voter_eta_fine_lowrange_1/va_t_rho_2.png` (y análogos para
  `rho_4`/`rho_8`): para la zona más lenta en relajar (`eta` chico, entre 0
  y 0.2), confirma el mismo patrón a `steps=5000`: el nivel medio ya está
  establecido bien antes de `t=1500`, con la comparativa 3000 vs. 5000 pasos
  en `eta=0.2` (`0.708` vs. `0.723` en `rho=2`, `0.663` vs. `0.650` en
  `rho=4`, `0.514` vs. `0.517` en `rho=8`) como evidencia cuantitativa de
  que no hay corrimiento sistemático más allá de `t=1500`.

En conjunto, estos tres grupos de gráficos son la base visual (`va(t)` con
la relajación ya visible) y las tres comparativas de duración (3000 vs.
5000, 3000 vs. 6000, y la reproducción independiente a 5000 pasos de
`eta=0.2`) son la base cuantitativa que respalda `t_eq=1500` como un corte
conservador y justificado, no solo un número elegido a ojo.

## Próximos pasos

Con el estudio dedicado del votante ya ejecutado (grilla refinada de 16
`eta`, `R=20`, `steps=3000`, densidades obligatorias y bajas), el siguiente
paso es decidir la definición de barra de error (desvío entre realizaciones
vs. error estándar) y, si se quiere respaldar con el mismo nivel de
evidencia la conclusión sobre `eta>1.5` en `rho=2,4,8`, correr también ahí
una comparación a mayor duración. Después de eso corresponde generar las
animaciones de los casos característicos (ruido bajo/alto) y avanzar con el
barrido definitivo (etapa 6) y las figuras (etapa 7).

## Pendientes y decisiones abiertas

- Falta el protocolo estadístico completo: promedio estacionario de los
  observables, elección de `t_eq`, realizaciones independientes y barras de
  error. Ahora hay un primer piloto (ver "Pilotos y protocolo estadístico"
  arriba) que aporta evidencia preliminar para cada uno de esos puntos, pero
  ninguno está cerrado.
- Falta decidir los valores productivos de stride (`--observables-stride`,
  `--trajectory-stride`) que se usarán en el barrido definitivo: el
  mecanismo ya está implementado y probado, y el piloto confirma que
  `--observables-stride 1` es liviano incluso con `N=800`, pero no se
  fijaron los números concretos de producción.
- Falta validar el consenso del votante sin ruido con los parámetros
  físicos completos del TP (densidad, `rc`, movimiento real): existe
  evidencia diagnóstica en un escenario simplificado (grafo completo,
  `N=20`, ver "Regresión del votante sin ruido" abajo), y ahora también
  evidencia piloto con los parámetros reales que muestra que 600 pasos
  **no alcanzan** para ver consenso con densidad y movimiento reales (ver
  "Pilotos y protocolo estadístico" arriba); falta un piloto dedicado más
  largo para ese caso específico.
- La grilla de `eta` y la conversión de densidades bajas ya quedaron
  resueltas después de este estado histórico; para clusters bajos se usa
  `N=32,16,11` con registro de densidad efectiva.
- Faltan los barridos definitivos y las figuras.
- Siguen abiertas las decisiones experimentales sobre `eta`, duración,
  realizaciones, semillas y barras de error (el formato de salida ya está
  congelado e implementado; ahora hay evidencia preliminar de piloto para
  cada una, registrada en `DECISIONES_PENDIENTES.md`).
- La conversión de densidades bajas a número entero de partículas quedó
  decidida el 2026-08-30: redondeo al entero más cercano (`N=32,16,11`).
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
