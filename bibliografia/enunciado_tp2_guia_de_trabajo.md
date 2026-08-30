# TP2 - Guía operativa del enunciado

> Basado en `TP2_Enunciado.pdf` (publicado en Campus el 13/08/2026). Este archivo organiza el pedido del trabajo; no reemplaza las guías de formato de presentaciones e informes citadas por la cátedra.

## 1. Objetivo

Implementar y estudiar un autómata *off-lattice* de bandadas de agentes autopropulsados en una caja cuadrada periódica de lado \(L=10\). Se analizan dos mecanismos de interacción:

1. **Modelo estándar de Vicsek:** cada agente toma la dirección promedio de todos sus vecinos y agrega ruido.
2. **Modelo de votante:** cada agente elige un único vecino al azar, copia su dirección y agrega ruido.

Para ambos modelos hay que estudiar cómo cambia el sistema al variar el ruido \(\eta\), en tres densidades:

\[
\rho\in\{2,4,8\},\qquad N=\rho L^2\in\{200,400,800\}.
\]

Los observables requeridos son la polarización \(v_a\) y la fracción \(S\) contenida en el cluster más grande.

## 2. Requisito de arquitectura

La simulación y la animación deben ser módulos independientes:

```text
motor de simulación -> archivos de texto por instante -> módulo de animación
```

El motor debe producir salida de texto con posiciones y velocidades (o información equivalente para reconstruirlas). La animación debe leer esos archivos, no ejecutar la simulación cuadro a cuadro. Así la velocidad de reproducción no depende del tiempo de cómputo.

## 3. Plan de trabajo por etapas

| Etapa | Qué hacer | Resultado verificable |
|---|---|---|
| 0. Diseño | Fijar parámetros comunes, barrido de \(\eta\), duración, semillas, cantidad de realizaciones y formato de salida. | Protocolo reproducible y tabla de parámetros. |
| 1. Motor Vicsek | Implementar movimiento, borde periódico, vecinos por radio y actualización sincrónica estándar. | Archivos de texto y casos simples coherentes. |
| 2. Medición | Calcular \(v_a(t)\), clusters y \(S(t)\); identificar transitorio y ventana estacionaria. | Series temporales y criterio explícito para \(t_\mathrm{eq}\). |
| 3. Barrido Vicsek | Repetir para cada \((\rho,\eta)\), con varias realizaciones independientes. | Promedios estacionarios y barras de error. |
| 4. Visualización | Animar casos característicos. Cada partícula es un vector velocidad, ubicado en su posición y coloreado por ángulo. | Animaciones seleccionadas para abrir cada estudio. |
| 5. Motor votante | Reemplazar solamente el promedio de vecinos por copia de un vecino aleatorio; mantener lo demás. | Salidas equivalentes y comparables con Vicsek. |
| 6. Barrido y comparación | Repetir mediciones, gráficos y animaciones para votante; superponer o contrastar ambos modelos. | Figuras comparativas respaldadas por datos. |
| 7. Rendimiento | Medir tiempos del CIM para tamaños de \(N\) similares a TP1 y contrastarlos con TP1. | Tabla/gráfico de tiempos y comparación razonada. |
| 8. Entrega | Preparar presentación, informe y ZIP final respetando formato y nombres. | Tres archivos en Campus y exposición oral. |

## 4. Estudios y figuras obligatorias

### A. Animaciones características

Para pocos casos representativos de cada estudio, construir animaciones con:

- un vector por partícula, con origen en \(\mathbf x_i(t)\) y dirección/módulo dados por \(\mathbf v_i(t)\);
- color del vector asociado a su ángulo;
- casos elegidos para hacer visible la dinámica, por ejemplo regímenes de bajo y alto ruido.

Las animaciones deben aparecer al comienzo de cada estudio, según la guía de presentaciones citada en el enunciado. No hace falta ni corresponde animar cada punto del barrido completo.

### B. Evolución temporal de la polarización

Para cada densidad y situaciones características de \(\eta\), graficar \(v_a(t)\). La figura tiene dos funciones:

1. mostrar la dinámica de relajación;
2. justificar desde qué instante comienza el estacionario usado para promediar.

Marcar en cada ejemplo con una línea vertical el inicio de la ventana estacionaria \(t_\mathrm{eq}\). Luego explicar cómo se obtiene el observable escalar, por ejemplo:

\[
\overline v_a=\frac{1}{M}\sum_{t=t_\mathrm{eq}}^{t_\mathrm{fin}}v_a(t),
\]

y cómo se promedia entre realizaciones. El enunciado exige que se explicite este criterio; no basta con presentar la curva final.

### C. Curva input vs. observable: \(\langle v_a\rangle\) vs. \(\eta\)

Para cada densidad, graficar el promedio estacionario de polarización contra el ruido:

\[
\eta\longmapsto\langle v_a\rangle_\mathrm{est}.
\]

Incluir barras de error y declarar qué representan. El gráfico debe distinguir claramente \(\rho=2,4,8\), ya sea con curvas/colores comunes o paneles comparables.

### D. Clusters: \(S(t)\) y \(\langle S\rangle\) vs. \(\eta\)

Un cluster es una componente conexa de la red de vecinos: puede unir dos partículas mediante una cadena de saltos entre pares separados a lo sumo por el radio de interacción \(r_c\). Si el mayor cluster tiene \(n_\max\) partículas:

\[
S(t)=\frac{n_\max(t)}{N}.
\]

Para cada densidad:

1. graficar \(S(t)\) para mostrar su evolución temporal;
2. estimar \(\langle S\rangle_\mathrm{est}\) y su desvío en la ventana estacionaria, con el mismo procedimiento de la polarización;
3. graficar \(\langle S\rangle_\mathrm{est}\) contra \(\eta\), con barras de error.

El borde periódico debe considerarse también al construir la red de vecinos; de lo contrario se partirían artificialmente clusters que cruzan un borde.

### E. Relación entre orden y conectividad

Graficar la polarización en función de la fracción de la componente gigante:

\[
\langle v_a\rangle_\mathrm{est}\ \text{vs.}\ \langle S\rangle_\mathrm{est}.
\]

Distinguir las tres densidades. Este gráfico no tiene \(\eta\) como eje: cada punto del barrido de ruido aporta un par \((\langle S\rangle,\langle v_a\rangle)\). Es una forma de estudiar si estar conectados en un cluster grande se relaciona con estar alineados globalmente.

### F. Repetición para el modelo de votante y comparación

Repetir los puntos A--E para el modelo de votante. Además de reportar sus resultados propios, comparar votante con Vicsek en las figuras de:

- evolución temporal de \(v_a\) (punto B);
- \(\langle v_a\rangle\) vs. \(\eta\) (punto C);
- resultados de clusters \(S\) (punto D);
- \(\langle v_a\rangle\) vs. \(\langle S\rangle\) (punto E).

La comparación es válida solo si usa los mismos parámetros y el mismo protocolo estadístico. Las conclusiones deben describir diferencias observadas en los datos, no suponerlas.

### G. Tiempos de ejecución del CIM

Elegir simulaciones con un número de partículas similar a los tamaños usados en TP1 y registrar el tiempo de ejecución del **CIM** (código implementado/motor de simulación). Comparar esos tiempos con los de TP1.

Para que la comparación sea interpretable, informar al menos: \(N\), cantidad de pasos, cantidad de realizaciones si aplica, equipo/entorno de medición y qué tramo se cronometró. No mezclar el tiempo de animación o de generación de gráficos con el tiempo del motor si el objetivo es medir el CIM.

## 5. Matriz mínima de experimentos

La matriz base contiene \(2\) modelos por \(3\) densidades por cada valor elegido de ruido:

\[
\{\text{Vicsek},\text{votante}\}\times\{2,4,8\}\times\{\eta_1,\ldots,\eta_K\}.
\]

Para cada combinación se necesitan varias realizaciones independientes y registros temporales suficientes para separar transitorio de estacionario. De cada corrida conviene conservar, al menos, \(v_a(t)\), \(S(t)\) y los cuadros necesarios para la animación. De cada combinación del barrido se reportan los promedios estacionarios y su incertidumbre.

## 6. Entregables y fecha indicados en el enunciado

El enunciado solicita:

1. presentación oral de **13 minutos**;
2. PDF de la presentación, sin animaciones embebidas y con links explícitos;
3. código fuente final del motor en un archivo ZIP pequeño (del orden de KB): sin historial, documentos ni outputs de simulación;
4. informe con las mismas secciones que la presentación y según `Formato_Informes.pdf`.

La fecha indicada es **04/09/2026 a las 13:00**, por Campus. Las presentaciones orales son ese mismo día. Los nombres requeridos son:

```text
SdS_TP2_2026Q2GXXCSS_Presentación
SdS_TP2_2026Q2GXXCSS_Codigo
SdS_TP2_2026Q2GXXCSS_Informe
```

Aquí `XX` es el número de grupo y `SS` la comisión (`S` o `S2`).

## 7. Lista final de control

- [ ] La salida del simulador es texto y la animación la consume de forma independiente.
- [ ] Se usaron condiciones periódicas tanto en el movimiento como en los vecinos/clusters.
- [ ] Se implementaron los dos modelos y se mantuvo comparable el resto de la configuración.
- [ ] Se estudiaron las tres densidades \(2,4,8\) y un barrido de \(\eta\).
- [ ] Las animaciones muestran vectores velocidad coloreados por ángulo.
- [ ] Las curvas temporales justifican el inicio del estacionario con una línea vertical.
- [ ] Las curvas contra \(\eta\) tienen barras de error y método de promedio declarado.
- [ ] Se presentaron \(S(t)\), \(\langle S\rangle\) vs. \(\eta\) y \(\langle v_a\rangle\) vs. \(\langle S\rangle\).
- [ ] Se compararon ambos modelos en los puntos B--E.
- [ ] Se midieron tiempos del CIM y se compararon con TP1.
- [ ] El informe y la presentación respetan las guías de formato citadas por la cátedra.

