# Guía de trabajo para agentes - Simulación de Sistemas, TP2

## Dónde estás

Este repositorio corresponde al Trabajo Práctico 2 de **Simulación de Sistemas**. El objetivo es implementar, medir y presentar un modelo de bandadas de agentes autopropulsados en espacio continuo (*off-lattice*).

No asumir que este es un TP de fluidos, *lattice gas*, Lattice Boltzmann o autómatas en grilla. Aunque aparecen en bibliografía de contexto, el trabajo implementa partículas puntuales que se mueven en una caja continua.

## Lectura obligatoria antes de desarrollar

Leer estos archivos en este orden:

1. [`bibliografia/enunciado_tp2_guia_de_trabajo.md`](bibliografia/enunciado_tp2_guia_de_trabajo.md): alcance, etapas, gráficos, entregables y checklist.
2. [`bibliografia/teoria_tp2_automatas_off_lattice.md`](bibliografia/teoria_tp2_automatas_off_lattice.md): ecuaciones, convenciones, observables, clusters, estadística y validaciones.
3. [`bibliografia/fuentes_recomendadas_tp2.md`](bibliografia/fuentes_recomendadas_tp2.md): qué fuente respalda cada decisión y qué bibliografía es solo contextual.

Los `.md` contienen el contexto operativo necesario; no es obligatorio buscar o copiar los PDF originales para implementar. Si se necesita justificar una afirmación en el informe, el tercer archivo identifica la fuente primaria o de contexto correspondiente.

Después de esas tres fuentes, leer también:

4. [`plan_desarrollo_tp2/README.md`](plan_desarrollo_tp2/README.md): índice maestro, orden de etapas y estado global.
5. [`plan_desarrollo_tp2/REVISION_FINAL_DE_ALCANCE.md`](plan_desarrollo_tp2/REVISION_FINAL_DE_ALCANCE.md): trazabilidad contra la cátedra y límites del camino principal.
6. [`plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`](plan_desarrollo_tp2/DECISIONES_PENDIENTES.md): decisiones que todavía requieren evidencia o elección del usuario.
7. El `.md` específico de la etapa que se va a ejecutar y todos los documentos de etapas de los que depende.

No comenzar una etapa leyendo solamente su archivo aislado: primero comprobar sus dependencias, su estado y las decisiones abiertas que puedan bloquearla.

## Especificación vinculante del modelo

La cátedra fija una caja cuadrada periódica de lado \(L=10\), radio de interacción \(r_c=1\), paso temporal \(\Delta t=1\) y rapidez constante \(v=0.03\).

Las densidades requeridas son \(\rho=2,4,8\), por lo que:

\[
N=\rho L^2\in\{200,400,800\}.
\]

Se deben implementar dos modelos, con el mismo dominio, parámetros y protocolo de medición:

- **Vicsek estándar:** usar el promedio vectorial de las direcciones de todos los agentes en el radio, incluida la propia partícula, y sumar ruido angular uniforme.
- **Votante ruidoso:** elegir al azar otra partícula dentro del radio y copiar su dirección, más ruido. Si no existe otro vecino, mantener la dirección y aplicar únicamente el ruido.

La actualización es **sincrónica**: toda dirección nueva se calcula desde el estado en \(t\). Las posiciones se actualizan con \(\mathbf v(t)\), no con \(\mathbf v(t+1)\) (*backward update*), y luego se repliegan con borde periódico.

Usar siempre la distancia mínima con periodicidad para vecinos y clusters. No promediar ángulos de manera aritmética: promediar \(\cos\theta\) y \(\sin\theta\) y recuperar el ángulo con `atan2`.

### Convención de ruido

Para el TP prevalece la convención de la teórica:

\[
\xi\sim\mathcal U[-\eta/2,\eta/2].
\]

No copiar directamente la normalización de \(\eta\) de artículos externos sin convertirla; está explicada en la guía teórica.

## Qué hay que medir

Los observables centrales son:

\[
v_a(t)=\frac{1}{Nv}\left|\sum_i\mathbf v_i(t)\right|,
\qquad
S(t)=\frac{n_{\max}(t)}{N}.
\]

Aquí \(S\) es la fracción en la componente conexa geométrica más grande. El cluster se construye uniendo pares separados por \(d_{ij}\le r_c\), con borde periódico.

Para cada combinación de modelo, densidad y ruido:

- guardar series temporales de \(v_a(t)\) y \(S(t)\);
- identificar y justificar el inicio estacionario \(t_\mathrm{eq}\);
- promediar en el estacionario y sobre realizaciones independientes;
- informar barras de error con una definición explícita;
- generar datos de posición y velocidad en texto para animaciones independientes.

Las figuras obligatorias y la comparación entre modelos están enumeradas en la guía del enunciado. No sustituirlas por análisis opcionales como susceptibilidad o escalado crítico.

## Arquitectura y entregable de código

El motor de simulación debe escribir salida de texto. El módulo de animación debe leer esa salida de manera independiente; nunca hacer depender el avance de la animación del tiempo de cómputo del motor.

Al entregar, el ZIP debe contener solo la versión final del código fuente del motor, sin historial, documentos ni resultados pesados. Mantener el formato de salida simple, estable y documentado para que gráficos y animaciones sean reproducibles.

## Validaciones mínimas antes de barrer parámetros

- Con posiciones aleatorias uniformes, el número medio inicial de **otros** vecinos debe aproximar \(\rho\pi r_c^2\): para \(r_c=1\), \(6.28\), \(12.57\) y \(25.13\) en las tres densidades.
- Verificar vecinos y clusters que cruzan un borde periódico.
- Verificar que el valor de \(v_a\) queda entre 0 y 1 y que vale 1 si todas las direcciones son idénticas.
- En el votante sin ruido, usar la llegada eventual al consenso polar como control de regresión; no confundir este ensayo con el barrido solicitado con ruido.
- Verificar que cambiar el orden de almacenamiento de las partículas no altera una actualización sincrónica.

## Decisiones que la cátedra no fija numéricamente

Antes de producir resultados definitivos, elegir, registrar y mantener constantes:

- grilla de valores de \(\eta\);
- cantidad de pasos de transitorio y de medición;
- cantidad de realizaciones independientes y semillas;
- definición de las barras de error (desvío entre realizaciones o error estándar);
- frecuencia de escritura de cuadros y formato exacto de los archivos de salida;
- entorno usado para cronometrar el motor frente a TP1.

Estas decisiones no deben presentarse como requisitos de la cátedra: son parte del protocolo experimental y deben justificarse con las series temporales.

## Seguimiento obligatorio del progreso en Markdown

Los archivos de `plan_desarrollo_tp2/` son documentos vivos y constituyen el estado operativo del proyecto. Todo agente que implemente, valide, mida o genere un entregable debe actualizarlos dentro de la misma tarea.

Reglas de marcado:

- Usar los checkboxes existentes de cada etapa: `[ ]` significa pendiente y `[x]` significa completado con evidencia.
- No marcar un ítem por haber escrito código o por estar “casi listo”. Solo marcarlo cuando se cumpla su criterio, se hayan ejecutado las verificaciones correspondientes y no queden fallos conocidos que lo invaliden.
- Si un ítem queda parcialmente hecho, mantenerlo en `[ ]` y añadir debajo una nota breve `Estado: en progreso`, indicando qué se completó, qué evidencia existe y qué falta.
- Si para describir correctamente el avance hacen falta subtareas, agregarlas como nuevos checkboxes debajo del ítem correspondiente. No borrar criterios originales ni reducir su alcance para poder marcarlos.
- Al cerrar una etapa, actualizar también la columna `Estado` de la tabla maestra en `plan_desarrollo_tp2/README.md`.
- Una etapa solo pasa a `[x]` cuando todos sus criterios de cierre están marcados, sus dependencias están completas y sus decisiones bloqueantes están resueltas.
- Registrar junto al checkbox o en una subsección `Evidencia` los comandos ejecutados, tests relevantes, archivos generados o tablas que demuestran el cierre. Evitar afirmaciones vagas como “tests OK” sin identificar qué se verificó.
- Si un cambio posterior invalida evidencia anterior —por ejemplo, cambia el motor, la regla, el formato o el protocolo— destildar los ítems y etapas afectados, explicar por qué y regenerar sus derivados.

No actualizar solamente un resumen conversacional: el estado persistente debe quedar reflejado en los `.md` del repositorio antes de terminar la tarea.

## Dependencias y puertas entre etapas

Antes de empezar una etapa:

1. Leer su criterio de entrada y de cierre.
2. Comprobar en el índice maestro que las etapas previas necesarias estén marcadas como completas.
3. Verificar directamente la evidencia o los artefactos de los que depende; no confiar solo en una marca histórica.
4. Revisar `DECISIONES_PENDIENTES.md` y confirmar que no haya una decisión abierta que bloquee el trabajo.
5. Si falta un resultado anterior que puede obtenerse dentro del alcance autorizado, completar primero esa dependencia y actualizar sus checks.
6. Si falta una decisión del usuario o una elección que cambia resultados, alcance, protocolo, arquitectura pública, formato o costo significativo, no avanzar suponiendo una respuesta.

Puertas principales:

- **Etapa 2 - Motor:** depende de que la especificación, reglas y formato mínimo de salida de la etapa 1 estén acordados.
- **Etapa 3 - Validaciones:** depende de un motor compilable de ambos modelos; ninguna corrida preliminar reemplaza estas validaciones.
- **Etapas 4-5 - Estadística y pilotos:** dependen del motor validado. Los pilotos producen la evidencia necesaria para proponer `eta`, `t_eq`, pasos, realizaciones y barras.
- **Etapa 6 - Barrido definitivo:** depende de validaciones completas y de que el usuario haya revisado/aceptado el protocolo experimental. También depende de resolver cómo convertir las densidades bajas a `N` entero.
- **Etapa 7 - Figuras:** depende de tablas completas del barrido. La inclusión de densidades bajas en el punto E depende de una aclaración explícita; no asumirla.
- **Etapa 8 - Rendimiento:** depende de definir los tamaños comparables con TP1, el entorno y el tramo que se va a cronometrar.
- **Etapa 9 - Entrega:** depende de figuras, animaciones, tiempos y datos finales, además de nombres, grupo/comisión y links aportados o aprobados por el usuario.

Una etapa posterior puede preparar estructura o tests aislados en paralelo solo si no consume ni congela resultados de una dependencia pendiente. Nunca presentar ese trabajo preparatorio como cierre de la etapa.

## Decisiones abiertas: consultar, no asumir

Cuando una decisión no esté fijada por la cátedra ni registrada como resuelta:

- detener el punto exacto que depende de ella;
- explicar al usuario qué se sabe, qué falta y qué etapa queda bloqueada;
- presentar alternativas concretas con sus consecuencias;
- dar una recomendación fundamentada cuando exista evidencia, diferenciándola de un requisito docente;
- invitar explícitamente al usuario a pensar y elegir;
- esperar la decisión antes de congelar el protocolo, producir el barrido definitivo o hacer cambios costosos derivados;
- registrar la decisión elegida, fecha, justificación y artefactos afectados en `DECISIONES_PENDIENTES.md` y en el `.md` de la etapa.

No hace falta consultar detalles internos reversibles que no cambian comportamiento, resultados ni interfaces —por ejemplo, el nombre de una variable local—. Sí se debe consultar cualquier elección que afecte:

- ecuaciones o interpretación del modelo;
- alcance de densidades, gráficos o entregables;
- grilla de ruido, transitorio, pasos, realizaciones, semillas o barras;
- formato público de los archivos una vez que tenga consumidores;
- criterios del benchmark;
- regeneración costosa de datos;
- una ambigüedad real del material de cátedra.

Si la evidencia necesaria todavía no existe, no pedir al usuario que elija a ciegas: ejecutar primero las corridas o verificaciones no bloqueadas, mostrar los resultados y recién entonces abrir la decisión.

## Comunicación obligatoria de pendientes

En toda actualización importante y en el cierre de cada tarea incluir una sección explícita de `Pendientes y decisiones abiertas`.

- Enumerar todo ítem incompleto, incertidumbre, decisión del usuario, fallo conocido o artefacto que deba regenerarse.
- Indicar qué etapa o entregable afecta y si bloquea el siguiente paso.
- Si no queda nada abierto dentro del alcance de la tarea, escribirlo expresamente: `No quedan pendientes conocidos para esta tarea`.
- Nunca ocultar un pendiente porque no impide compilar o porque pertenece a una etapa posterior.
- No declarar el objetivo global terminado mientras exista una decisión bloqueante, una combinación faltante, una validación sin evidencia o un entregable derivado desactualizado.

## Límites de alcance

No incorporar al motor elementos de la bibliografía de contexto: grilla hexagonal, bits de ocupación, colisiones FHP/LGCA, *streaming* LBM, conservación de masa/momento, número de Reynolds, obstáculos, fuerzas de atracción/repulsión, campo visual anisotrópico o regla de los \(k\) vecinos más cercanos.

La evidencia empírica de bandadas reales puede ser útil para una introducción del informe, pero no modifica la regla métrica isotrópica por radio que exige este TP.

## Forma de trabajo

Antes de editar código existente, inspeccionar su estructura, dependencias, comandos de ejecución y cambios no comprometidos. Mantener cambios acotados, verificarlos y actualizar la documentación cuando se cambie una convención, un formato de salida o el protocolo experimental.

Al comenzar una tarea, indicar qué etapa se está abordando, de qué resultados previos depende y qué checks se espera cerrar. Al terminar, actualizar los Markdown correspondientes, resumir la evidencia y comunicar siempre los pendientes o decisiones abiertas según las reglas anteriores.
