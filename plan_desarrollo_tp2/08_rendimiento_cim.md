# Etapa 8 - Tiempos del CIM

## Objetivo

Cumplir el punto G: registrar tiempos del código implementado para cantidades de partículas similares a las usadas en TP1 y compararlos con TP1.

## Decisiones que deben registrarse

- valores de `N` elegidos;
- cantidad de pasos;
- cantidad de repeticiones del cronometraje;
- equipo, sistema, compilador y opciones de compilación;
- tramo exacto que se cronometra.

La cátedra no fija esos valores numéricos, pero exige que la comparación sea interpretable.

## Medición

- Usar el mismo equipo y entorno para TP1 y TP2.
- Elegir tamaños de `N` iguales o similares a los de TP1; incluir `200,400,800` si son comparables con los tamaños anteriores.
- Preferir instrumentar dentro de ambos motores la misma operación CIM: reconstrucción de celdas y generación de vecinos. Registrar cuántas llamadas entraron en cada media.
- Excluir de esa ventana el arranque del proceso, generación inicial, trayectoria, log escalar, animación, gráficos y reconstrucciones adicionales hechas solo para medir observables.
- Igualar, siempre que los dos TP lo permitan, `N`, `L`, `rc`, periodicidad, `M` y la convención geométrica de partículas puntuales. Si alguna no puede igualarse, declararla antes de interpretar la diferencia.
- No incluir animación ni generación de gráficos.
- Si se comparan tramos o parámetros diferentes, declararlo y no interpretar la diferencia como una mejora del CIM.
- Repetir las mediciones suficientes veces para informar una tendencia estable; la cantidad se fija en el protocolo, no viene dada por la cátedra.
- Definir antes de medir cómo se tratan calentamiento y valores atípicos. Si se descartan mediciones, aplicar una regla idéntica, conservar el conteo descartado y justificarla; no recortar datos solo para que las barras se vean mejor.
- La geometría de entrada afecta el número de pares candidatos. Idealmente usar configuraciones comparables; si TP1 usa posiciones uniformes y TP2 estados evolucionados/agrupados, informar esa diferencia y acompañarla con el número medio de vecinos o pares candidatos.

## Resultado

Preparar una tabla o gráfico con:

```text
N, pasos, tiempo TP1, tiempo TP2, dispersión de repeticiones, entorno
```

La conclusión debe limitarse a lo realmente medido. No es obligatorio ajustar una complejidad ni comparar CIM contra fuerza bruta en esta etapa.

## Criterio de cierre

- [ ] Los `N` son similares a los de TP1.
- [ ] Se informa qué tramo fue cronometrado.
- [ ] Animación y gráficos quedan fuera del tiempo.
- [ ] TP1 y TP2 se miden en el mismo entorno o se declara la limitación.
- [ ] Los parámetros geométricos y las configuraciones de entrada son comparables o sus diferencias están cuantificadas.
- [ ] El tratamiento de calentamiento/atípicos y el número de mediciones están documentados.
- [ ] Tabla/gráfico y conclusión son reproducibles.
