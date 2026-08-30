# Etapa 9 - Informe, presentación y entrega

## Objetivo

Cerrar el trabajo con una narrativa fiel a los datos, una exposición de 13 minutos y un ZIP de código pequeño y reproducible.

## Progreso parcial (2026-08-30)

- [x] Se generó una síntesis interna del estado para ubicar al grupo frente al enunciado: `output/pdf/estado_actual_tp2_explicado.pdf`. Explica el alcance, motor, validaciones, piloto de 108 corridas, decisiones tomadas y pendientes, y la secuencia que falta hasta la entrega.
  - Evidencia: el PDF se renderizó y revisó en cinco páginas A4; `pdfinfo` confirmó cinco páginas y la extracción de texto confirmó contenido en todas. En la misma revisión se ejecutó `cmake --build build` y `ctest --test-dir build --output-on-failure`, con 11/11 pruebas aprobadas.
  - Alcance: artefacto de orientación interna. No reemplaza el informe final, la presentación ni los resultados definitivos y por ello los criterios de cierre de esta etapa permanecen abiertos.

## Estructura narrativa sugerida

1. Sistema y pregunta: cómo ruido, densidad y regla de interacción afectan orden y conectividad.
2. Modelo: dominio, condiciones periódicas, ruido, Vicsek, votante y movimiento backward.
3. Implementación: sincronía, CIM, componentes conexas y texto desacoplado.
4. Validación: borde, vecinos medios, fuerza bruta, observables y consenso votante sin ruido.
5. Protocolo: grilla de `eta`, pilotos, `t_eq`, realizaciones y barras.
6. Animaciones/casos característicos.
7. Polarización temporal y estacionaria.
8. Clusters, incluida extensión de densidades.
9. Relación `va(S)` y comparación de modelos.
10. Rendimiento CIM.
11. Conclusiones limitadas por la evidencia.

## Qué debe quedar escrito sin ambigüedad

- `xi ~ U[-eta/2,eta/2]` y `eta` en radianes.
- Posición avanza con `v(t)`.
- Vicsek incluye a sí misma; votante elige otra partícula.
- `S=n_max/N` y clusters usan borde periódico.
- Cómo se eligió `t_eq`.
- Primero promedio temporal por realización, luego promedio entre realizaciones.
- Qué significan las barras y cuántas realizaciones hay.
- Densidad nominal, `N` y densidad efectiva de los casos `1/pi`.
- Qué parte del tiempo se cronometró.

## Discusión responsable

- Hablar de tendencias observadas, no de resultados “forzados” por teoría.
- No llamar transición crítica precisa a un cambio localizado por una grilla gruesa.
- No dar más decimales que la resolución/variabilidad permite.
- Distinguir conectividad de alineamiento.
- No incorporar análisis extra como si fueran parte del enunciado.
- Indicar `N=11,16,32` al presentar las densidades adicionales.
- Si `S` satura en densidades altas, presentarlo como resultado y usar las bajas para ampliar el estudio, no reemplazar las obligatorias.

## Presentación de 13 minutos

La exposición debe respetar los 13 minutos indicados y seguir las mismas secciones que el informe. Abrir cada estudio con la animación o un fotograma y enlace explícito, según la guía de presentaciones. Ensayar con cronómetro sin eliminar evidencia obligatoria para incluir análisis adicionales.

La presentación y el informe son documentos autocontenidos: no dejar una definición, cantidad de repeticiones o parámetro solamente en uno suponiendo que el lector consultará el otro. Numerar las diapositivas. En la presentación, ubicar los parámetros al costado de cada figura y no dentro de un título/caption del gráfico; usar ejes legibles y fuente de al menos 20. La versión usada para exponer integra las animaciones; el PDF entregado las reemplaza por un fotograma representativo y un enlace explícito.

## Trazabilidad de números

Crear una tabla o script que alimente directamente valores citados en texto. Antes de compilar entregables:

- buscar placeholders, `TODO`, enlaces vacíos y legajos incompletos;
- comparar títulos/captions con parámetros reales;
- verificar que cada figura se generó con el commit/config final;
- revisar que informe y presentación no citen números de pilotos;
- comprobar consistencia de símbolos (`va`, `S`, `eta`, `rho`).

Usar una única tabla de protocolo como fuente para duración, `R`, semillas, `t_eq`, barras y grilla. Después de cualquier cambio del motor o protocolo, invalidar datos y derivados afectados antes de volver a compilar. La revisión debe comparar también las ecuaciones y reglas escritas contra el código final: que el motor se haya corregido no actualiza automáticamente una ecuación vieja del informe.

## ZIP de código

Incluir solo el código fuente final del motor y lo mínimo para compilar/ejecutar, según el enunciado. Excluir:

- `.git` e historial;
- PDFs, documentación extensa y presentaciones;
- datos, figuras, GIFs y logs;
- binarios y objetos;
- entornos virtuales/cachés.
- archivos del sistema/editor como `.DS_Store`.

Verificar el ZIP extrayéndolo en un directorio temporal limpio, compilando y ejecutando self-tests/smoke test. Documentar formato de salida en un README breve si el límite lo permite.

## Revisión visual final

Renderizar informe y presentación completos y revisar todas las páginas:

- texto no recortado ni superpuesto;
- figuras legibles y nítidas;
- ecuaciones correctas;
- numeración/referencias consistentes;
- links clicables;
- portada, autores, comisión y fecha correctos.

## Criterio de cierre

- [ ] Informe y presentación contienen los mismos resultados finales.
- [ ] Todas las figuras obligatorias aparecen y son legibles.
- [ ] Animaciones publicadas y enlaces probados.
- [ ] Método estadístico y actualización backward declarados.
- [ ] Claims compatibles con incertidumbre y tamaño finito.
- [ ] Benchmark describe exactamente qué mide.
- [ ] Ecuaciones, reglas y tabla de protocolo coinciden entre código, informe, presentación y figuras.
- [ ] ZIP limpio recompila y pasa tests desde cero.
- [ ] Nombres de archivos y entrega coinciden con el enunciado.
