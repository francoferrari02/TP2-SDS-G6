# Fuentes recomendadas: relevancia para TP2

Este registro evita mezclar bibliografía de contexto con especificaciones del trabajo. Las instrucciones vinculantes para la implementación y los entregables siguen siendo `TP2_Enunciado.pdf` y la teórica de la cátedra.

| Fuente | Relevancia | Aporte aplicado | Dónde quedó incorporado |
|---|---|---|---|
| `Teorica_2.pdf` | Directa | Definición del modelo off-lattice de Vicsek, \(v=0.03\), \(r_c=1\), ruido, polarización y actualización simultánea. | `teoria_tp2_automatas_off_lattice.md` |
| `TP2_Enunciado.pdf` | Vinculante | Dos modelos, densidades, observables, gráficos, animaciones, rendimiento y entrega. | `enunciado_tp2_guia_de_trabajo.md` |
| `NovelTypePhaseTransition2.pdf` — Vicsek *et al.* (1995) | Directa para el modelo estándar | Fuente primaria de la caja periódica off-lattice, regla de promedio angular, ruido, parámetros \(\eta,\rho,v\) y polarización. | Secciones 2 y 6 de `teoria_tp2_automatas_off_lattice.md` |
| `2021-PhysRevE-104-034111.pdf` — Loscar, Baglietto y Vázquez | Directa para el modelo de votante | Copia de un vecino aleatorio, caso sin vecinos, comparación entre actualización paralela y secuencial, susceptibilidad y advertencia sobre la normalización del ruido. | Secciones 5, 5.1 y 7 de `teoria_tp2_automatas_off_lattice.md` |
| `Flocking dynamics with voter-like interactions.pdf` — Baglietto y Vázquez | Directa como validación del votante sin ruido | Confirma borde periódico, radio métrico, actualización *backward*, consenso polar sin ruido y relación entre clustering y alineamiento. | Secciones 3, 5 y 9 de `teoria_tp2_automatas_off_lattice.md` |
| `M3AS_20SUPPL.P1491.pdf` — Cavagna *et al.* (2010) | Contextual, interpretativa | Revisa mediciones en bandadas reales y encuentra evidencia de interacción topológica (cantidad fija de vecinos) en estorninos. | Aclara una alternativa empírica, pero no cambia el radio métrico impuesto por el TP. |
| `PhysicsToday.pdf` — Feder (2007) | Contextual, divulgativa | Resume resultados del proyecto StarFlag: interacción topológica con aproximadamente 6–7 vecinos y anisotropía en bandadas de estorninos. | Refuerza los límites empíricos del modelo del TP; no cambia su implementación. |
| `02_Lattice Gas Models.pdf` | Contextual, no operativo | Distingue los gases de red FHP: partículas en retícula triangular, estados booleanos y colisiones que conservan masa y momento. | Se usa para descartar su aplicación al algoritmo del TP; no se añade una regla de FHP. |
| `Cellular-Automata-Models-Complexity-Stephen-Wolfram-Article.pdf` — Wolfram (1984) | Contextual, conceptual | Presenta los AC como sistemas discretos con reglas locales y actualización temporal; clasifica patrones simples, periódicos, caóticos y complejos. | Aporta contexto a la introducción, sin cambios al modelo ni a las mediciones del TP. |
| `Chapter_7_LatticeBoltzman.pdf` — Satoh | Contextual, no operativo | Describe Lattice Boltzmann D2Q9 para flujo de un fluido alrededor de un cilindro, con distribuciones en nodos, colisión, streaming y fronteras. | Se usa para descartar LBM como solución del TP; no se añade al motor. |
| `lattice gas cellular automata and lattice boltzmann models.pdf` | Contextual, no operativo | Manual amplio de LGCA/LBM: colisiones, propagación, conservación de masa/momento, ecuación de Boltzmann y Navier-Stokes. | Confirma la distinción con el TP; no se incorpora ningún algoritmo de fluido. |

## Qué no debe transferirse desde *Lattice Gas Models*

El capítulo de *lattice gas* explica el modelo FHP para fluidos. En él las partículas ocupan nodos de una red triangular, tienen seis velocidades discretas y evolucionan por propagación y colisiones que conservan masa y momento. También usa tablas de bits, sólidos y condiciones de rebote.

Nada de eso corresponde al TP2: aquí las partículas tienen posiciones y ángulos continuos, velocidad de módulo fijo, interacción por radio y una regla de alineamiento o copia. Por lo tanto, no se deben implementar grilla hexagonal, bits de ocupación, colisiones FHP, conservación de momento ni *bounce-back* para este trabajo.

Su único valor directo es conceptual: refuerza que el modelo del TP es un autómata con regla local y actualización temporal, pero de tipo **off-lattice**, no un gas de red.

## Aportes contextuales de Wolfram y Lattice Boltzmann

El artículo de Wolfram (1984) ayuda a ubicar el concepto de autómata celular: reglas locales simples, aplicadas repetidamente, pueden originar comportamientos estacionarios, periódicos, crecientes o complejos. Esa idea es útil para motivar por qué se estudian series temporales y animaciones en simulación. Sin embargo, el artículo trata autómatas discretos, especialmente unidimensionales, y su clasificación de clases no es una clasificación de los regímenes del modelo de Vicsek. No corresponde etiquetar las bandadas del TP como “clase 1--4” ni usar sus reglas elementales.

El capítulo de Lattice Boltzmann es aún más distante del objetivo: representa un fluido mediante funciones de distribución \(f_\alpha(\mathbf r,t)\) sobre una red D2Q9, y alterna operaciones de colisión y *streaming*. Sus condiciones de borde, relajación, número de Reynolds, coeficiente de arrastre y obstáculo circular responden a un problema de dinámica de fluidos. El TP no calcula campos de densidad o velocidad de un fluido y no contiene cilindros u obstáculos.

El manual extenso de LGCA/LBM llega a la misma conclusión desde una formulación más general: los LGCA se diseñan para conservar masa y momento y los LBM aproximan ecuaciones hidrodinámicas como Navier-Stokes. La velocidad de cada agente del TP, en cambio, se redefine por alineamiento o copia y ruido; no conserva el momento total. Por eso sus herramientas de colisión, expansión de Chapman-Enskog y distribuciones de equilibrio quedan fuera de alcance.

En ambos casos, la enseñanza transferible es metodológica: especificar sin ambigüedad la condición inicial, las condiciones de contorno y la regla de actualización, y medir la evolución antes de inferir un régimen estacionario. Esos principios ya están contemplados en las guías del TP; no agregan experimentos obligatorios.

## Interacciones métricas y topológicas

El estudio empírico de Cavagna *et al.* encuentra que en bandadas de estorninos la interacción es compatible con una regla **topológica**: cada ave responde aproximadamente a un número fijo de vecinos, sin que la distancia absoluta sea el criterio principal. Es una alternativa importante en sistemas reales, pero no es la regla de este trabajo.

El TP define vecinos mediante el radio de interacción \(r_c\), por lo que la red cambia según la distancia: es una interacción **métrica**. No se debe reemplazar por “los \(k\) vecinos más cercanos”, ni comparar los resultados como si ambas formulaciones fueran equivalentes. El artículo puede citarse, si resulta útil en la introducción del informe, como motivación de que el modelo es una idealización deliberada.

La nota de *Physics Today* aporta el mismo contraste en formato divulgativo y menciona que el efecto topológico observado en estorninos alcanza aproximadamente a 6–7 vecinos, además de una distribución anisotrópica de vecinos. Esos hechos **no** autorizan a modificar el TP: no se agregan fuerzas explícitas de atracción/repulsión, un campo visual direccional ni una regla de vecinos más cercanos. Solo sirven para explicar que el modelo métrico isotrópico de Vicsek es una idealización controlada de una bandada real.

## Nota metodológica del artículo de votante

El artículo analiza también límites de campo medio, partículas estáticas en redes y escalado de tamaño finito. Es información útil para interpretar resultados, pero esos experimentos no son requerimientos adicionales del TP. En particular, el TP fija \(L=10\), \(v=0.03\) y tres densidades; no exige estimar exponentes críticos ni hacer extrapolación termodinámica.

El resultado cualitativo que sí ayuda a discutir las curvas es que, para partículas móviles en espacio continuo, el modelo de votante ruidoso puede mostrar una transición entre orden y desorden a ruido finito. La posición del cruce y la forma de las curvas dependen de \(v\), densidad y tamaño, por lo que no deben anticiparse valores numéricos a partir del artículo, que usa \(\rho=0.5\) y otra convención de ruido.
