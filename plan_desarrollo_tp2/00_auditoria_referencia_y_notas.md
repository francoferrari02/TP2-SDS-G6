# Etapa 0 - Auditoría del repositorio de referencia y lectura de las notas

## Objeto auditado

- Repositorio: `https://github.com/juan43963/TP2-SDS-G5`
- Rama: `main`
- Commit revisado: `b912936da5f3b06c8c28b55645d0c924d3fad6ae`
- Fecha del commit: 27/08/2026 18:49:42 -0300
- Alcance: motor C++, tests, scripts Python, informe y presentación compilados.

Seguimiento posterior:

- Nuevo `main` revisado: [`413dcef55e7abd81349a5e706d1381fe54aa6ca0`](https://github.com/juan43963/TP2-SDS-G5/commit/413dcef55e7abd81349a5e706d1381fe54aa6ca0).
- Fecha del nuevo extremo: 29/08/2026 15:37:59 -0300.
- Rango comparado: `b912936..413dcef`, compuesto por tres commits: [`a0c3493`](https://github.com/juan43963/TP2-SDS-G5/commit/a0c34931f40b5ee5fdaf99c06f00b32b390a876c), [`cda0eb8`](https://github.com/juan43963/TP2-SDS-G5/commit/cda0eb8eeb5f525faa4206415962731898040558) y [`413dcef`](https://github.com/juan43963/TP2-SDS-G5/commit/413dcef55e7abd81349a5e706d1381fe54aa6ca0).
- Alcance nuevo: motor, tests, barrido, análisis, animación, benchmark, Makefile, informe, presentación y bibliografía contextual.
- Verificación local del nuevo extremo: `make clean all test` terminó con 14.770 verificaciones y 0 fallas; `python3 python/sweep.py --selftest` también terminó correctamente.

La compilación y el self-test C++ terminaron correctamente con 14.765 verificaciones. Eso prueba coherencia interna, pero no conformidad con el modelo: varios tests codifican como comportamiento esperado decisiones que contradicen la especificación vinculante.

## Diagnóstico ejecutivo

En el commit original auditado, el repositorio tenía una arquitectura aprovechable como referencia conceptual, pero sus resultados numéricos debían descartarse para nuestro TP. Dos errores cambiaban la dinámica: movía con la orientación nueva y el votante podía copiarse a sí mismo aun cuando tenía otros vecinos. Corregir cualquiera de ellos obliga a regenerar todos los datos, figuras y conclusiones afectados.

Al 29/08 corrigieron el movimiento en el motor, pero no la regla del votante ni el corte `d <= rc`. Por eso la situación mejoró, pero el repositorio actualizado todavía no es una fuente válida de resultados numéricos para nuestro desarrollo.

Además, el protocolo estadístico y el benchmark no justifican algunas afirmaciones del informe. La conclusión correcta no es “copiar y retocar”, sino comenzar con una especificación congelada, pruebas que representen esa especificación y un piloto antes del barrido costoso.

## Seguimiento de los cambios del 29/08/2026

### Correcciones reales y prácticas aprovechables

- **Movimiento corregido en el motor:** `Simulation::step()` ahora desplaza con `theta(t)` y confirma `theta(t+1)` después. Esto coincide con la teórica y elimina uno de los dos defectos críticos de la auditoría original.
- **Grilla de ruido compartida:** el nuevo `sweep.py` usa una grilla final idéntica para Vicsek y votante. Es una buena guarda de comparabilidad, aunque sus 39 valores concretos siguen siendo una decisión del otro grupo y no se adoptan para nuestro TP sin pilotos propios.
- **Identidad de corrida más segura:** la cantidad de pasos forma parte del nombre del archivo y el agregador exige `steps+1` filas. Esto evita que un piloto corto pise silenciosamente una corrida larga.
- **Densidades bajas tratadas por separado:** el repositorio afirma haber observado transitorios más largos para `1/pi`, `1/(2pi)` y `1/(3pi)` y por eso les asigna otra duración. El valor `10000` no es transferible mientras su votante siga siendo distinto, pero sí confirma que esas densidades deben pilotarse por separado y que no corresponde extrapolarles el `t_eq` de `rho=2,4,8`.
- **Benchmark mejor instrumentado:** el cronómetro se movió al interior del motor, alrededor de `grid.rebuild()`, excluyendo inicio del proceso, escritura de trayectoria, gráficos y reconstrucciones usadas solamente para medir `S`. Además igualan `L`, `rc`, periodicidad, `M` y partículas puntuales con TP1.
- **Salidas organizadas y animaciones derivadas del barrido:** los gráficos se separan por tipo y los `eta` característicos se seleccionan desde el resumen ya medido, en vez de lanzar un minipiloto que pueda contaminar la producción.
- **Dependencias de headers en C++:** el Makefile agrega `-MMD -MP`, evitando enlazar objetos compilados contra versiones viejas de un header.

Estas ideas se incorporan como controles de nuestro proceso, no como resultados numéricos ni requisitos adicionales de la cátedra.

El nuevo `analyze.py` atribuye además a una consulta de clase tres indicaciones visuales: no usar grilla de fondo, no mezclar `va` con `S` en la misma figura y presentar primero cada modelo por separado antes de la comparación. Las dos últimas son compatibles con una narrativa clara y no cambian datos; sin embargo, esas frases no aparecen en el enunciado ni en la copia de la Guía de Presentaciones revisada. Se registran para confirmación antes de congelar las figuras, no como requisitos vinculantes.

### Errores o riesgos que continúan

| Prioridad | Estado al 29/08 | Consecuencia para nosotros |
|---|---|---|
| Crítica | El votante todavía sortea en `{i} union vecinos_externos`; los tests siguen llamando correcta a la autoinclusión | Sus corridas del votante, incluidas las de densidad baja, no sirven como referencia numérica |
| Alta | `withinRadius` continúa usando `d2 < rc^2` | Sigue contradiciendo `d <= rc`; su comparación CIM-fuerza bruta no lo detecta porque ambos caminos reutilizan el mismo predicado |
| Alta | No agregaron un test manual del movimiento *backward* | La corrección existe en código, pero no tiene una prueba de regresión que falle si alguien la revierte |
| Alta | El informe todavía escribe movimiento con `theta(t+1)`, vecindario autoinclusivo para ambos modelos, `K=5`, 2000 pasos y el benchmark viejo; la presentación ya dice movimiento *backward*, `K=10` y duraciones distintas | Código, informe y presentación no describen el mismo experimento; ningún PDF debe darse por actualizado solo porque compile |
| Alta | El driver agrega y escribe `summary.csv` aun si hay fallos, sin exigir `n_seeds == R` por punto | Una matriz incompleta puede llegar silenciosamente a las figuras; producción debe tener una puerta de completitud que falle de forma ruidosa |
| Alta | El Makefile considera vigente `summary.csv` si el binario no cambió, pero no depende de `sweep.py`, la grilla, el protocolo ni una huella de configuración | Cambiar pasos, semillas, estadística o grilla puede reutilizar datos obsoletos |
| Media | `plot_va_vs_S` mantiene `x=va`, `y=S` | El eje sigue invertido respecto de “polarización en función de componente gigante” |
| Media | El punto E se genera para las seis densidades | Mantiene la ampliación no confirmada; no resuelve nuestra decisión abierta de alcance |
| Media | Inicialización y dinámica reinician generadores con la misma semilla | Persiste el riesgo de correlacionar el comienzo del flujo aleatorio de la condición inicial con el de la dinámica |
| Media | El barrido manda la trayectoria a `/dev/null`, pero el motor igualmente formatea cada cuadro | Desperdicia cómputo; conviene un modo real `trajectory=none` |
| Media | La susceptibilidad sigue calculándose como `N*va_std^2` a partir del desvío de medias entre realizaciones y continúa en el informe | No es el estimador definido en la teoría y, además, es un estudio fuera del alcance pedido |
| Baja | Se agregó `.DS_Store` y varios PDF contextuales | Refuerza la necesidad de controlar el contenido del ZIP y de no convertir bibliografía contextual en requisitos del motor |

### Límite de lo que puede inferirse

El repositorio no versiona sus datos crudos del barrido. Por eso se puede comprobar el código y que los documentos compilan, pero no verificar que todas las figuras y números hayan sido regenerados con el motor corregido. Además, los valores que afirman para `t_eq`, cantidad de pasos o número de semillas fueron obtenidos con una regla de votante que sigue siendo distinta de la vinculante. Se conservan como indicios para diseñar pilotos, nunca como decisiones resueltas para nuestro desarrollo.

## Qué hicieron bien y conviene conservar como idea

- Separaron motor, análisis y animación.
- Usaron C++20 para el motor y texto plano para las salidas.
- Implementaron borde periódico con distancia mínima.
- Usaron promedio circular de senos y cosenos en Vicsek.
- Aplicaron el ruido `U[-eta/2,eta/2]` en un único punto compartido.
- Usaron doble buffer para no mezclar orientaciones viejas y nuevas.
- Reutilizaron una búsqueda de vecinos tipo Cell Index Method.
- Calcularon `S` como tamaño de la mayor componente conexa dividido por `N`.
- Separaron las medias por realización antes de agregar semillas.
- Guardaron semillas deterministas y archivos por corrida.
- Produjeron animaciones a partir de trayectorias ya escritas.

Estas prácticas no validan sus números; solo indican buenas decisiones de ingeniería que pueden reimplementarse correctamente.

## Hallazgos que invalidan o debilitan resultados

| Prioridad | Hallazgo | Evidencia en el commit | Consecuencia | Decisión para nuestro desarrollo |
|---|---|---|---|---|
| Crítica | Movimiento con orientación nueva | `simulation.cpp` calcula velocidad desde `thetaNew_`; informe Ec. 1 usa `theta(t+dt)` | Cambian posiciones, vecindades, transición, `va` y `S` | Mover con `theta(t)` y confirmar `theta(t+1)` después |
| Crítica | Votante autoinclusivo | `voterHeading` sortea en `{i} union vecinos` | Reduce la tasa efectiva de copia y no implementa la regla pedida | Sortear solo otra partícula; aislada = dirección propia + ruido |
| Alta | Tests confirman la variante errónea | Los tests celebran la autoinclusión; no hay prueba *backward* | Una suite verde da falsa seguridad | Escribir pruebas desde las ecuaciones de cátedra |
| Alta | Corte estacionario fijo sin demostración | Se descarta siempre el primer 50% de 2.000 pasos | El votante lento puede seguir en transitorio | Elegir `t_eq` con pilotos y usar un corte conservador validado |
| Alta | Solo 5 semillas sin una justificación suficiente | `DEFAULT_K_SEEDS=5` | La precisión de las barras no quedó establecida antes del barrido | Elegir y justificar la cantidad de realizaciones con corridas preliminares; la cátedra no fija un número |
| Alta | Susceptibilidad mal estimada | `chi=N*va_std^2`, donde `va_std` es el desvío de medias de corridas | No equivale a `N(<va^2>-<va>^2)` de muestras estacionarias | Omitirla en nuestro TP porque no está solicitada |
| Alta | Benchmark no compara la misma operación | TP1: búsqueda; TP2: paso completo + formato/I/O; además `L` difiere | No permite atribuir diferencias al CIM | Instrumentar la sección CIM en ambos motores y usar mismos `N`/entorno |
| Media | Criterio estricto `d < rc` | `withinRadius` usa `< rc^2` | Contradice `d <= rc`; falla en casos deterministas de frontera | Usar `<=` y probar igualdad exacta |
| Media | Grilla baja mezclada con todo el barrido | Las densidades extra entran en `DEFAULT_RHOS` para todos los análisis | Amplía polarización fuera de lo pedido y aumenta costo | Separar barrido base y extensión de clusters |
| Media | Eje invertido en relación orden-conectividad | `plot_va_vs_S` usa `x=va`, `y=S` | No sigue literalmente “`va` en función de `S`” | Usar `x=<S>`, `y=<va>`; un punto por `eta` |
| Media | Densidad nominal ocultando redondeo | Etiqueta `1/pi` con `N=32` y `L=10` | La densidad efectiva es 0.32 | Informar nominal, `N` y efectiva |
| Media | “Percolación pura” medida después de dinámica | El barrido `eta=0` corre el motor durante miles de pasos | Las posiciones ya están correlacionadas; no es un grafo geométrico inicial | No usar ese extra como validación de percolación estática |
| Media | Corrientes RNG reiniciadas con la misma semilla | Inicialización y dinámica crean generadores separados con igual semilla | Puede correlacionar números de inicialización y dinámica | Derivar subsemillas/streams independientes y estables por partícula |
| Baja | El barrido formatea trayectorias hacia `/dev/null` | No hay modo real de deshabilitar trayectoria | Desperdicia tiempo y contamina benchmark | Añadir `--trajectory none` y frecuencias configurables |
| Baja | Salida de trayectoria sin metadatos ni `N` | Se infieren frames por cantidad de columnas | Parser frágil ante truncamiento o cambios | Cabecera versionada y filas con `t,id,x,y,vx,vy` |

## Observaciones sobre informe y presentación

- Tienen una estructura visual consistente y muestran las familias principales de gráficos.
- Los valores y conclusiones se apoyan en el motor incorrecto, por lo que no se pueden reutilizar.
- La documentación interna de consultas reconoce que la convención de movimiento difiere de la teórica y cuantifica el impacto, pero el informe final solo presenta la variante elegida sin destacar el conflicto. Para nuestro trabajo la ecuación de cátedra prevalece.
- Se presentan valores de `eta_c` con tres decimales aunque su propia auditoría reconoce variaciones grandes entre grupos de semillas. Es precisión aparente.
- La presentación aún contiene “enlace a publicar antes de la entrega” para los videos.
- El gráfico temporal de la presentación se rotula `eta=0`, mientras el informe y las figuras mencionan valores positivos; hay una inconsistencia de comunicación.
- La comparación de tiempos declara que las magnitudes no son comparables. Esa honestidad es buena, pero no reemplaza la medición solicitada.

## Traducción de las notas del profesor a requisitos accionables

### “Tenemos que hacer barrido para tener un eta” / “para varios ruidos”

No se debe elegir un único ruido. Se hace un barrido con varios valores de `eta`, elegidos y justificados con corridas preliminares. El producto obligatorio es una curva, no un “eta ganador”. La cátedra no fija el rango ni el paso numérico.

### “Hacer todas las combinaciones”

Cada valor de la grilla final debe correrse para ambos modelos y cada densidad obligatoria. No vale usar distintas combinaciones aisladas para llenar gráficos. La extensión baja se ejecuta para clusters en ambos modelos.

### “Promediás varias realizaciones”

Cada punto debe surgir de realizaciones independientes. Primero se promedia el estacionario dentro de cada realización; después se promedian esas medias. Los tiempos correlacionados de una misma corrida no cuentan como realizaciones.

### “Un gráfico para las distintas densidades”

Las curvas deben distinguir `rho=2,4,8` con colores/paneles consistentes. Para clusters se agregan las tres densidades bajas sin contaminar la figura principal de polarización.

### “Casos bien distintos, nos quedaríamos con 2”

Para series temporales y animaciones no se necesita representar cada punto. Se seleccionarán al menos dos regímenes claramente distintos por modelo: bajo ruido/ordenado y alto ruido/desordenado. Si el tiempo lo permite, se agrega un caso cercano al cambio como diagnóstico, no como reemplazo de los dos extremos.

### “En el CIM... se parece más a fuerza bruta” / “¿qué generan en clusters?”

El CIM reduce los pares candidatos al construir vecinos. El cluster no es una celda ni un grupo de vecinos directos: es una componente conexa transitiva. Después de obtener las aristas vecinas, el mayor componente puede calcularse con BFS/DFS o `union-find`, tal como admite la guía teórica. Comparar todos contra todos puede conservarse únicamente como referencia de validación en casos pequeños.

### “¿Cómo es la relación de S y va?” / “polarización vs componente gigante”

Cada `eta` produce el par `(<S>,<va>)`. El gráfico requerido usa `S` en el eje x y `va` en el eje y, distingue densidad/modelo y puede colorear los puntos por `eta`. Una componente gigante grande mide conectividad espacial; polarización alta mide alineamiento. Ninguna implica automáticamente la otra, por eso se comparan.

### “Gigante es de 0 a 1” / “cluster más grande vs ruido”

El observable es una fracción: `S=n_max/N`, con `1/N <= S <= 1` si `N>0`. Hay que mostrar `S(t)` y `<S>_est` vs. `eta`, no el tamaño absoluto sin normalizar.

### Aclaración de densidades

Se mantienen `rho=2,4,8` en todo el TP. La aclaración amplía el punto D de clusters con `1/pi`, `1/(2pi)`, `1/(3pi)`. El punto E pide explícitamente distinguir tres densidades, por lo que el camino mínimo usa allí `rho=2,4,8`. Extender también el punto E requiere una confirmación adicional de la cátedra y no se toma como obligación.

## Criterio de cierre de esta etapa

- [x] Repositorio externo identificado por commit.
- [x] Código, tests, scripts y entregables contrastados con las ecuaciones vinculantes.
- [x] Prácticas reutilizables separadas de resultados inválidos.
- [x] Notas del profesor convertidas en requisitos verificables.
- [x] Alcance de las densidades bajas explicitado con `N` entero y densidad efectiva.
- [x] Seguimiento del 29/08 comparado desde el commit original y trasladado a las etapas afectadas.
