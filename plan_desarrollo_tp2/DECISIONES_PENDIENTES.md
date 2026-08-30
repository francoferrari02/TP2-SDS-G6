# Decisiones pendientes del TP2

## Cómo usar este archivo

Este es el registro único de decisiones que no pueden resolverse suponiendo. Todo agente debe revisarlo antes de comenzar una etapa y actualizarlo cuando una decisión se abre o se cierra.

Estados:

- `[ ]` pendiente: todavía requiere evidencia, aclaración de cátedra o elección del usuario.
- `[x]` resuelta: registrar decisión, fecha, fundamento y archivos/etapas afectados.

Una recomendación del agente no equivale a una decisión. Mientras el checkbox siga abierto, no ejecutar trabajo definitivo que dependa de ella.

## Ambigüedades de alcance y parámetros

- [ ] **Conversión de densidades bajas a `N` entero.**
  - Contexto: con `L=10`, `N=rho L^2` no es entero para `rho=1/pi,1/(2pi),1/(3pi)`.
  - Convención provisional a discutir: redondeo al entero más cercano, dando `N=32,16,11`, y registro de densidad efectiva.
  - Bloquea: barrido definitivo de clusters de la etapa 6.
  - Decisión del usuario/cátedra: pendiente.

- [ ] **Alcance de las densidades bajas en el punto E (`<va>` vs. `<S>`).**
  - Contexto: la aclaración dice extender densidades “solo para el estudio de Cluster”, mientras el punto E original pide distinguir tres densidades.
  - Camino mínimo actual: usar las densidades bajas en el punto D y mantener `rho=2,4,8` en el punto E.
  - Bloquea: únicamente una posible ampliación del gráfico E, no el motor ni el barrido principal.
  - Decisión del usuario/cátedra: pendiente.

## Protocolo experimental

Estas decisiones deben proponerse después de las corridas preliminares de la etapa 5 y ser aceptadas antes del barrido definitivo:

- [ ] **Grilla final de valores de `eta`.**
  - Evidencia necesaria: corridas preliminares que muestren regímenes de ruido diferenciados y resolución suficiente de las curvas.
  - Bloquea: etapa 6.

- [ ] **Cantidad de pasos de transitorio y de medición / criterio de `t_eq`.**
  - Evidencia necesaria: series `va(t)` y `S(t)` con relajación y ventana estacionaria identificables.
  - Bloquea: promedios definitivos de etapas 6-7.

- [ ] **Cantidad de realizaciones independientes y semillas.**
  - Evidencia necesaria: variabilidad observada en pilotos y presupuesto de cómputo.
  - Bloquea: etapa 6.

- [ ] **Definición de barras de error.**
  - Opciones admitidas por la guía: desvío entre realizaciones o error estándar.
  - Bloquea: agregación y figuras definitivas.

- [ ] **Frecuencia y formato final de salida de texto.**
  - Requisito fijo: debe permitir animación independiente con posiciones y velocidades/información equivalente.
  - Bloquea: congelar consumidores y producir trayectorias definitivas.

## Rendimiento y entrega

- [ ] **Protocolo de comparación de tiempos con TP1.**
  - Falta elegir `N`, pasos/repeticiones, entorno y tramo cronometrado.
  - Bloquea: etapa 8.

- [ ] **Datos administrativos y enlaces finales.**
  - Falta confirmar grupo, comisión, integrantes/números requeridos y destino de las animaciones.
  - Bloquea: cierre de etapa 9.

- [ ] **Indicaciones visuales atribuidas a la consulta de clase.**
  - Contexto: el repositorio de referencia actualizado afirma que la cátedra pidió gráficos sin grilla de fondo, `va` y `S` en figuras separadas y resultados de cada modelo por separado antes de la comparación.
  - Verificado en la guía escrita: sí aparecen la fuente mínima 20, ausencia de título/*caption* dentro de figuras de presentación, parámetros al costado, puntos visibles y animación integrada en vivo/fotograma con link en PDF. Las otras tres indicaciones solo constan como comentario del repositorio externo.
  - Bloquea: congelar el diseño visual final de etapas 7 y 9; no bloquea motor, pilotos ni producción de datos.
  - Decisión del usuario/cátedra: pendiente.

## Evidencia externa que no resuelve decisiones

El seguimiento del repositorio de referencia hasta `413dcef` muestra que ese grupo usa `N=32,16,11`, amplía el punto E a densidades bajas, adopta 39 valores de `eta`, 10 semillas, 2000/10000 pasos y un corte del 50%. Ninguna de esas elecciones prueba una indicación de cátedra ni reemplaza nuestros pilotos. Además, su regla de votante sigue permitiendo autoelección, por lo que sus tiempos de relajación y resultados del votante no son transferibles. Todos los checkboxes correspondientes permanecen abiertos.

## Decisiones resueltas

Mover aquí los ítems cerrados conservando su texto, y agregar:

```text
Decisión:
Fecha:
Fundamento/evidencia:
Etapas y archivos afectados:
Usuario que aprobó:
```
