# Teoría para TP2: autómata off-lattice de bandadas

> Fuente principal: `Teorica_2.pdf`, diapositivas 39--46. Esta guía desarrolla la parte de la teórica que se usa directamente en el TP2. Las primeras diapositivas presentan autómatas celulares **en grilla**; el modelo a implementar aquí es *off-lattice*: las partículas se mueven en posiciones continuas.

## 1. Marco: autómatas celulares y modelo off-lattice

Un autómata celular clásico tiene celdas discretas, estados discretos, actualización sincrónica y una regla local. En una grilla 2D se suelen usar vecindades de Von Neumann o Moore.

El modelo de Vicsek conserva la idea esencial de una regla local y actualización simultánea, pero no discretiza el espacio. Por eso:

- cada agente es puntual y tiene posición continua \(\mathbf{x}_i(t)=(x_i(t),y_i(t))\);
- cada agente lleva una velocidad de módulo fijo \(v\) y orientación \(\theta_i(t)\);
- los vecinos se definen geométricamente por distancia, no por celdas adyacentes;
- todas las orientaciones nuevas se calculan desde el mismo estado \(t\), antes de sobrescribir ninguna. Esto evita que el orden del arreglo cambie el resultado.

## 2. Dominio, parámetros y condición inicial

El sistema vive en una caja cuadrada de lado \(L\), con condiciones periódicas de contorno. Para la teórica:

\[
\Delta t=1,\qquad v=0.03,\qquad r_c=1.
\]

Sus variables de control son:

\[
\rho=\frac{N}{L^2},\qquad v,\qquad \eta,
\]

donde \(\rho\) es la densidad, \(N\) el número de partículas y \(\eta\) la amplitud de ruido angular. Equivalentemente,

\[
N=\rho L^2.
\]

La formulación original de Vicsek identifica precisamente \(\eta\), \(\rho\) y \(v\) como los parámetros libres para un tamaño de sistema fijado. En este TP, \(L=10\), \(v=0.03\) y \(r_c=1\) están fijados; el estudio cambia \(\eta\) y compara tres valores de \(\rho\).

Para el TP, como \(L=10\), las tres densidades solicitadas implican:

| \(\rho\) | Cálculo de \(N=\rho L^2\) | \(N\) |
|---:|---:|---:|
| 2 | \(2\times10^2\) | 200 |
| 4 | \(4\times10^2\) | 400 |
| 8 | \(8\times10^2\) | 800 |

En \(t=0\), se muestrean posiciones uniformes en \([0,L)\times[0,L)\) y ángulos aleatorios uniformes en \([0,2\pi)\). La velocidad inicial es

\[
\mathbf v_i(0)=v\,[\cos\theta_i(0),\sin\theta_i(0)].
\]

## 3. Borde periódico y distancia mínima

Salir por un borde equivale a entrar por el opuesto. Tras mover una coordenada, se la repliega mediante

\[
x_i\leftarrow x_i\bmod L,\qquad y_i\leftarrow y_i\bmod L.
\]

Para decidir vecindad, no sirve siempre la distancia euclídea directa: dos partículas cerca de bordes opuestos pueden ser vecinas. Para cada componente, la separación mínima es

\[
\delta x_{ij}=x_j-x_i-L\,\operatorname{round}\!\left(\frac{x_j-x_i}{L}\right),
\]

\[
\delta y_{ij}=y_j-y_i-L\,\operatorname{round}\!\left(\frac{y_j-y_i}{L}\right),
\qquad
d_{ij}=\sqrt{\delta x_{ij}^2+\delta y_{ij}^2}.
\]

El conjunto de vecinos de \(i\), incluyéndose a sí misma como especifica la teórica, es

\[
\mathcal N_i(t)=\{j: d_{ij}(t)\le r_c\}.
\]

### Chequeo útil de la búsqueda de vecinos

Con posiciones inicialmente uniformes y borde periódico, el número esperado de **otros** vecinos de una partícula es aproximadamente el área del disco de interacción por la densidad:

\[
\langle k\rangle_0\simeq \rho\pi r_c^2.
\]

Para \(r_c=1\), los valores esperados al inicio son \(2\pi\approx6.28\), \(4\pi\approx12.57\) y \(8\pi\approx25.13\) para \(\rho=2,4,8\), respectivamente. En una realización finita habrá fluctuaciones; si el promedio de muchas inicializaciones se aparta marcadamente de esos valores, se debe revisar el radio, el borde periódico o el criterio de inclusión. Si se cuenta a la propia partícula, el resultado aumenta en uno.

## 4. Regla de evolución del modelo estándar de Vicsek

### 4.1 Movimiento

Las posiciones avanzan con la velocidad del instante actual:

\[
\mathbf x_i(t+1)=\mathbf x_i(t)+\mathbf v_i(t)\Delta t,
\]

y luego se aplican las condiciones periódicas.

### 4.2 Alineamiento local

No deben promediarse los ángulos como números ordinarios (por ejemplo, \(1^\circ\) y \(359^\circ\) no promedian \(180^\circ\)). Se promedian los vectores unitarios de las direcciones vecinas:

\[
C_i(t)=\frac{1}{|\mathcal N_i|}\sum_{j\in\mathcal N_i}\cos\theta_j(t),
\qquad
S_i(t)=\frac{1}{|\mathcal N_i|}\sum_{j\in\mathcal N_i}\sin\theta_j(t),
\]

\[
\bar\theta_i(t)=\operatorname{atan2}\big(S_i(t),C_i(t)\big).
\]

El ruido angular es independiente por partícula y por paso:

\[
\xi_i(t)\sim\mathcal U\left[-\frac{\eta}{2},\frac{\eta}{2}\right].
\]

La nueva orientación y velocidad son

\[
\theta_i(t+1)=\bar\theta_i(t)+\xi_i(t),
\qquad
\mathbf v_i(t+1)=v[\cos\theta_i(t+1),\sin\theta_i(t+1)].
\]

Finalmente, conviene normalizar \(\theta_i\) al intervalo elegido, por ejemplo \([0,2\pi)\), usando módulo \(2\pi\).

### 4.3 Actualización correcta

En cada paso se usan arreglos nuevos para \(\theta(t+1)\), \(\mathbf v(t+1)\) y, si corresponde, \(\mathbf x(t+1)\). La regla conceptual es:

1. con el estado completo en \(t\), construir las vecindades;
2. calcular todas las direcciones nuevas con los ángulos de \(t\);
3. avanzar posiciones con las velocidades de \(t\) y replegarlas;
4. reemplazar el estado entero por el de \(t+1\).

Así se respeta la actualización simultánea indicada en la teórica.

## 5. Modelo de votante ruidoso

La geometría, el movimiento, el radio, el ruido y la actualización sincrónica no cambian. Solo cambia la regla de interacción.

En lugar de formar el promedio vectorial, cada partícula \(i\) escoge al azar un vecino \(j_i\) dentro del radio de interacción y copia su orientación. El artículo de referencia del TP implementa al vecino como **otra** partícula dentro del disco: define

\[
\mathcal N_i^\ast(t)=\{j\ne i:d_{ij}(t)\le r_c\}.
\]

Si \(\mathcal N_i^\ast\ne\varnothing\), entonces

\[
j_i\sim\operatorname{Uniforme}(\mathcal N_i^\ast),
\qquad
\theta_i(t+1)=\theta_{j_i}(t)+\xi_i(t),
\]

\[
\mathbf v_i(t+1)=v[\cos\theta_i(t+1),\sin\theta_i(t+1)].
\]

Si no hay otro agente en el radio, el artículo indica que la partícula solo cambia por ruido:

\[
\mathcal N_i^\ast=\varnothing
\quad\Longrightarrow\quad
\theta_i(t+1)=\theta_i(t)+\xi_i(t).
\]

Esto no contradice la regla estándar de Vicsek presentada en la teórica, donde se incluye la propia partícula al calcular el promedio. Son reglas distintas y el código debe documentar esa diferencia. Para el votante conviene seguir la definición del artículo, pues es la referencia [2] citada explícitamente por el enunciado.

El artículo define primero una actualización paralela, como la indicada arriba, aunque usa actualización secuencial aleatoria para parte de sus análisis de escalado. Para el TP debe prevalecer la actualización sincrónica de la teórica: calcular todas las elecciones, ruidos y direcciones nuevas a partir del estado \(t\), y recién entonces reemplazar el estado. No hay que trasladar la actualización secuencial del artículo al motor salvo que la cátedra lo pida expresamente.

La regla de posición utilizada tanto por la teórica como por el trabajo sin ruido de Baglietto y Vázquez es la actualización *backward*: se desplaza con \(\mathbf v_i(t)\), no con la velocidad recién calculada \(\mathbf v_i(t+1)\). Esta convención ya está expresada en la ecuación de movimiento de la sección 4.1 y debe mantenerse igual en ambos modelos.

La diferencia física es importante: Vicsek combina la información de todos los vecinos; el votante transmite la dirección de un único vecino al azar. La comparación debe aislar ese cambio, manteniendo iguales \(L,\rho,v,r_c,\eta\), protocolo temporal y cantidad de realizaciones.

### 5.1 Atención a la convención de ruido

La teórica y el enunciado describen el ruido como un ángulo uniforme de amplitud total \(\eta\):

\[
\xi\sim\mathcal U[-\eta/2,\eta/2].
\]

El artículo de Loscar *et al.* usa otro parámetro adimensional, también llamado \(\eta\), con

\[
\xi\sim\mathcal U[-\pi\eta,\pi\eta),\qquad 0<\eta<1.
\]

Por lo tanto, si se quisiera reproducir literalmente las figuras del artículo, las amplitudes se relacionan por \(\eta_{\text{teórica}}=2\pi\eta_{\text{artículo}}\). Para el TP se debe conservar la convención de la cátedra y no copiar valores numéricos de \(\eta\) del artículo sin convertirlos.

## 6. Observable primario: polarización

La teórica define el parámetro de orden de velocidad (polarización) como

\[
v_a(t)=\frac{1}{Nv}\left|\sum_{i=1}^{N}\mathbf v_i(t)\right|.
\]

Como todos los módulos valen \(v\), también puede calcularse directamente a partir de los ángulos:

\[
v_a(t)=\frac{1}{N}
\sqrt{\left(\sum_{i=1}^{N}\cos\theta_i(t)\right)^2+
      \left(\sum_{i=1}^{N}\sin\theta_i(t)\right)^2}.
\]

Sus límites interpretables son:

- \(v_a\approx0\): direcciones sin orden macroscópico; las contribuciones vectoriales se cancelan.
- \(v_a\approx1\): bandada polarizada; las partículas apuntan casi en una dirección común.

Este observable es la velocidad media normalizada introducida en el trabajo original de Vicsek. Es el parámetro apropiado porque el modelo **no conserva el momento total**: en cada actualización las direcciones se redefinen por alineamiento local y ruido. Por ello no corresponde usar conservación de momento como prueba de corrección, a diferencia de los modelos de gas de red discutidos en la otra bibliografía.

En un sistema finito, un estado aleatorio no da necesariamente cero exacto: el residual típico es del orden de \(N^{-1/2}\). Por eso se informan promedios y dispersión entre realizaciones, no una sola corrida.

## 7. Transitorio, estacionario y estimación escalar

La señal elemental que genera el simulador es una serie temporal, por ejemplo \(v_a(t)\). Antes de promediar hay que identificar un tiempo de relajación \(t_\mathrm{eq}\), a partir del cual la serie fluctúa alrededor de un régimen estable. El estimador temporal de una realización es

\[
\overline{v}_a^{(r)}=
\frac{1}{M}\sum_{t=t_\mathrm{eq}}^{t_\mathrm{fin}}v_a^{(r)}(t),
\qquad
M=t_\mathrm{fin}-t_\mathrm{eq}+1.
\]

Para \(R\) realizaciones independientes:

\[
\langle v_a\rangle=
\frac{1}{R}\sum_{r=1}^{R}\overline v_a^{(r)},
\qquad
s_{v_a}=\sqrt{\frac{1}{R-1}\sum_{r=1}^{R}
\left(\overline v_a^{(r)}-\langle v_a\rangle\right)^2}.
\]

La barra de error debe declararse con claridad. Dos elecciones usuales son la desviación entre realizaciones \(s_{v_a}\), que muestra variabilidad, o el error estándar \(s_{v_a}/\sqrt R\), que muestra precisión del promedio. No son intercambiables. Las muestras temporales correlacionadas no deben contarse como realizaciones independientes.

Como diagnóstico complementario (no exigido explícitamente por el TP), el artículo de votante usa la susceptibilidad de la polarización:

\[
\chi=N\left(\langle v_a^2\rangle-\langle v_a\rangle^2\right).
\]

Aquí los corchetes representan promedios estacionarios y entre realizaciones. Un máximo de \(\chi\) al variar \(\eta\) localiza, para un tamaño finito, la región de mayores fluctuaciones y sirve para elegir con mejor criterio dónde refinar el barrido de ruido. No reemplaza las curvas obligatorias \(\langle v_a\rangle\) vs. \(\eta\).

## 8. Clusters y componente gigante

En un instante dado se construye un grafo no dirigido:

\[
G(t)=(V,E),\qquad V=\{1,\ldots,N\},\qquad
(i,j)\in E\iff d_{ij}(t)\le r_c.
\]

Un *cluster* es una componente conexa de este grafo: dos partículas pertenecen al mismo cluster si hay una cadena de vecinos que las conecta, aunque no estén a distancia \(r_c\) entre sí. Si \(n_\max(t)\) es el número de nodos de la componente más grande, el observable pedido es

\[
S(t)=\frac{n_\max(t)}{N},\qquad \frac1N\le S(t)\le1.
\]

El cálculo debe usar la misma distancia periódica de la sección 3. Una búsqueda en profundidad/anchura sobre el grafo o una estructura *union-find* obtiene \(n_\max\). Para el estacionario se usa exactamente el mismo esquema de promedio temporal y entre realizaciones que para \(v_a\), sustituyendo \(v_a\) por \(S\).

## 9. Qué se espera observar

El ruido \(\eta\) actúa como una perturbación angular: al aumentarlo, en general desarma el orden colectivo y la polarización disminuye. La densidad modifica cuántos contactos existen y, por tanto, el alcance efectivo del alineamiento. A baja densidad y bajo ruido pueden aparecer grupos coherentes que no necesariamente constituyen una bandada global. La teórica muestra precisamente estos regímenes y propone estudiar \(v_a\) en función de \(\eta\).

Estos son comportamientos a medir, no resultados que deban forzarse: las conclusiones del informe deben apoyarse en curvas, series temporales, animaciones y barras de error producidas por las simulaciones.

### Caso de validación: votante sin ruido

El modelo de votante sin ruido \((\eta=0)\) no crea direcciones nuevas: cada actualización solo copia una dirección existente. Por lo tanto, para una caja finita el estado de consenso polar \(v_a=1\) es un control muy útil del motor; el trabajo de Baglietto y Vázquez encuentra que se alcanza tras la dinámica de copia y movimiento. No es un resultado del barrido con ruido ni hay que exigir llegar a consenso para una cantidad de pasos arbitraria, pero sí sirve como prueba de regresión.

Durante ese acercamiento pueden formarse agregados espaciales de partículas con direcciones similares. Esto da una interpretación física a medir simultáneamente \(v_a(t)\), \(S(t)\) y animaciones: un cluster grande puede aumentar la conectividad local y favorecer la copia de su dirección. El TP pide medir el cluster geométrico más grande; no debe confundirse con el número de direcciones distintas estudiado en el artículo.

## 10. Referencias de las fuentes entregadas

1. T. Vicsek, A. Czirók, E. Ben-Jacob, I. Cohen y O. Shochet, *Novel type of phase transition in a system of self-driven particles*, Physical Review Letters 75(6), 1226 (1995).
2. E. S. Loscar, G. Baglietto y F. Vazquez, *Noisy multistate voter model for flocking in finite dimensions*, Physical Review E 104(3), 034111 (2021).
3. *Lattice Gas Models*, capítulo 2 de una introducción a autómatas celulares y gases de red (bibliografía de cátedra).
4. G. Baglietto y F. Vazquez, *Flocking dynamics with voter-like interactions*, arXiv:1608.08231 (2019).
